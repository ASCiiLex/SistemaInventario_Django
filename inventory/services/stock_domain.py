from django.db import transaction
from django.core.exceptions import ValidationError


class StockDomainService:
    """
    🔥 CORE DEL DOMINIO DE INVENTARIO (ORQUESTADOR)

    - Sin lógica duplicada
    - Sin efectos secundarios en models
    - Flujo controlado
    """

    @staticmethod
    def execute(movement, user=None):

        # 🔥 imports lazy
        from inventory.models.stock import StockItem

        # 🔒 idempotencia
        if movement.idempotency_key:
            existing = movement.__class__.objects.filter(
                organization=movement.organization,
                idempotency_key=movement.idempotency_key
            ).first()

            if existing:
                return existing

        with transaction.atomic():
            movement.full_clean()
            movement.save()  # 🔥 IMPORTANTE → signals funcionan

            StockDomainService._apply_stock(movement, StockItem)

        StockDomainService._post_commit(movement, user)

        return movement

    # =========================
    # STOCK
    # =========================

    @staticmethod
    def _get_stock_for_update(StockItem, movement, location):
        return StockItem.objects.select_for_update().get(
            organization=movement.organization,
            product=movement.product,
            location=location,
        )

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
    def _apply_stock(movement, StockItem):

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

        # 🔥 SOLO EVENTOS → nada de lógica duplicada

        emit_event(
            Events.MOVEMENT_CREATED,
            {
                "product": movement.product,
                "message": f"Movimiento de stock en {movement.product.name}",
            }
        )

        sync_all_notifications(movement.organization)