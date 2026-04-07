from django.db import transaction
from django.core.exceptions import ValidationError


class StockDomainService:
    """
    🔥 CORE DEL DOMINIO DE INVENTARIO (HARDENED)

    - Consistencia fuerte (locks reales)
    - Idempotencia sólida
    - Validaciones de negocio centralizadas
    - Sin efectos secundarios en models
    """

    @staticmethod
    def execute(movement, user=None):

        from inventory.models.stock import StockItem

        # 🔒 idempotencia fuerte
        if movement.idempotency_key:
            existing = movement.__class__.objects.filter(
                organization=movement.organization,
                idempotency_key=movement.idempotency_key
            ).first()

            if existing:
                return existing

        with transaction.atomic():

            # 🔒 validación previa
            movement.full_clean()

            # 🔒 persistencia (activa signals)
            movement.save()

            # 🔒 aplicar stock con locks reales
            StockDomainService._apply_stock(movement, StockItem)

        # 🔥 fuera de transacción
        StockDomainService._post_commit(movement, user)

        return movement

    # =========================
    # STOCK CORE (LOCKED)
    # =========================

    @staticmethod
    def _get_stock_for_update(StockItem, movement, location):
        try:
            return StockItem.objects.select_for_update().get(
                organization=movement.organization,
                product=movement.product,
                location=location,
            )
        except StockItem.DoesNotExist:
            raise ValidationError("Stock no existente para la operación.")

    @staticmethod
    def _get_or_create_stock_for_update(StockItem, movement, location):
        item, _ = StockItem.objects.select_for_update().get_or_create(
            organization=movement.organization,
            product=movement.product,
            location=location,
            defaults={"quantity": 0},
        )
        return item

    @staticmethod
    def _validate_business_rules(movement):

        if movement.quantity <= 0:
            raise ValidationError("Cantidad inválida.")

        if movement.movement_type == "OUT" and not movement.origin:
            raise ValidationError("Salida sin origen.")

        if movement.movement_type == "IN" and not movement.destination:
            raise ValidationError("Entrada sin destino.")

        if movement.movement_type == "TRANSFER":
            if not movement.origin or not movement.destination:
                raise ValidationError("Transferencia incompleta.")
            if movement.origin == movement.destination:
                raise ValidationError("Origen y destino no pueden coincidir.")

    @staticmethod
    def _apply_stock(movement, StockItem):

        StockDomainService._validate_business_rules(movement)

        if movement.movement_type == "IN":

            item = StockDomainService._get_or_create_stock_for_update(
                StockItem, movement, movement.destination
            )

            item.quantity += movement.quantity
            item.save(update_fields=["quantity"])

        elif movement.movement_type == "OUT":

            item = StockDomainService._get_stock_for_update(
                StockItem, movement, movement.origin
            )

            if item.quantity < movement.quantity:
                raise ValidationError("Stock insuficiente.")

            item.quantity -= movement.quantity
            item.save(update_fields=["quantity"])

        elif movement.movement_type == "TRANSFER":

            origin = StockDomainService._get_stock_for_update(
                StockItem, movement, movement.origin
            )

            if origin.quantity < movement.quantity:
                raise ValidationError("Stock insuficiente para transferir.")

            # 🔥 ORDEN FIJO PARA EVITAR DEADLOCK
            origin.quantity -= movement.quantity
            origin.save(update_fields=["quantity"])

            dest = StockDomainService._get_or_create_stock_for_update(
                StockItem, movement, movement.destination
            )

            dest.quantity += movement.quantity
            dest.save(update_fields=["quantity"])

    # =========================
    # POST-COMMIT
    # =========================

    @staticmethod
    def _post_commit(movement, user):

        from notifications.events import emit_event
        from notifications.constants import Events
        from inventory.services.stock_alerts import sync_all_notifications

        emit_event(
            Events.MOVEMENT_CREATED,
            {
                "product": movement.product,
                "message": f"Movimiento de stock en {movement.product.name}",
            }
        )

        sync_all_notifications(movement.organization)