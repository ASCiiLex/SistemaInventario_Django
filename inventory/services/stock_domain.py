from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Sum

from django.db import connection


class StockDomainService:

    @staticmethod
    def execute(movement, user=None):

        from inventory.models.stock import StockItem

        if movement.idempotency_key:
            existing = movement.__class__.objects.filter(
                organization=movement.organization,
                idempotency_key=movement.idempotency_key
            ).first()

            if existing:
                return existing

        try:
            with transaction.atomic():

                # 🔒 LOCK DURO POR PRODUCTO (fila lógica)
                StockDomainService._lock_product_scope(movement)

                movement.full_clean()
                movement.save_base(raw=True)  # ⚠️ evita recursión

                # 🔒 LOCK GLOBAL TODAS LAS LOCATIONS DEL PRODUCTO
                StockItem.objects.select_for_update().filter(
                    organization=movement.organization,
                    product=movement.product
                )

                StockDomainService._apply_stock(movement, StockItem)

                # 🔒 VALIDACIÓN GLOBAL (dentro del lock)
                StockDomainService._validate_global_stock(movement, StockItem)

        except IntegrityError:
            if movement.idempotency_key:
                return movement.__class__.objects.get(
                    organization=movement.organization,
                    idempotency_key=movement.idempotency_key
                )
            raise

        transaction.on_commit(lambda: StockDomainService._post_commit(movement, user))

        return movement

    @staticmethod
    def _lock_product_scope(movement):
        """
        🔥 LOCK LÓGICO POR PRODUCTO (evita race conditions cross-location)
        Funciona incluso si no existen filas en StockItem
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_xact_lock(%s)",
                [hash(f"{movement.organization_id}:{movement.product_id}")]
            )

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

            locations = sorted(
                [movement.origin, movement.destination],
                key=lambda l: l.id
            )

            locked_items = {}

            for loc in locations:
                locked_items[loc.id] = StockDomainService._get_or_create_stock_for_update(
                    StockItem, movement, loc
                )

            origin = locked_items[movement.origin.id]
            dest = locked_items[movement.destination.id]

            if origin.quantity < movement.quantity:
                raise ValidationError("Stock insuficiente para transferir.")

            origin.quantity -= movement.quantity
            origin.save(update_fields=["quantity"])

            dest.quantity += movement.quantity
            dest.save(update_fields=["quantity"])

    @staticmethod
    def _validate_global_stock(movement, StockItem):
        total = StockItem.objects.filter(
            organization=movement.organization,
            product=movement.product
        ).aggregate(total=Sum("quantity"))["total"] or 0

        if total < 0:
            raise ValidationError("Inconsistencia detectada: stock total negativo.")

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