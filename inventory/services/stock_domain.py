from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from django.db import connection

import logging
import time
import os

logger = logging.getLogger("inventory.domain")
metrics = logging.getLogger("inventory.metrics")

from core.observability.metrics import domain_events_total, errors_total
from prometheus_client import Histogram

stock_execution_time = Histogram(
    "stock_execution_seconds",
    "Tiempo de ejecución de movimientos de stock"
)


class StockDomainService:

    @staticmethod
    def execute(movement, user=None):

        from inventory.models.stock import StockItem

        start_time = time.time()

        logger.info("stock.execute.start", extra={
            "product_id": movement.product_id,
            "org_id": getattr(movement.organization, "id", None),
            "type": movement.movement_type,
            "qty": movement.quantity,
        })

        if not movement.organization and movement.product:
            movement.organization = movement.product.organization

        if movement.idempotency_key:
            existing = movement.__class__.objects.filter(
                organization=movement.organization,
                idempotency_key=movement.idempotency_key
            ).first()

            if existing:
                logger.warning("stock.idempotent.hit", extra={
                    "movement_id": existing.id,
                    "key": movement.idempotency_key
                })
                return existing

        try:
            with transaction.atomic():

                StockDomainService._lock_product_scope(movement)

                movement.full_clean()

                if not movement.created_at:
                    movement.created_at = timezone.now()

                movement.save_base(raw=True)

                StockItem.objects.select_for_update().filter(
                    organization=movement.organization,
                    product=movement.product
                )

                StockDomainService._apply_stock(movement, StockItem)

                StockDomainService._validate_global_stock(movement, StockItem)

        except ValidationError as e:
            errors_total.labels(type="validation_error").inc()

            logger.warning("stock.validation.error", extra={
                "errors": str(e),
                "product_id": movement.product_id,
                "type": movement.movement_type,
            })

            raise

        except IntegrityError:
            errors_total.labels(type="integrity_error").inc()

            logger.exception("stock.integrity.error")

            if movement.idempotency_key:
                return movement.__class__.objects.get(
                    organization=movement.organization,
                    idempotency_key=movement.idempotency_key
                )
            raise

        transaction.on_commit(lambda: StockDomainService._post_commit(movement, user))

        duration = time.time() - start_time

        domain_events_total.labels(
            event_type=f"stock:{movement.movement_type.lower()}"
        ).inc()

        stock_execution_time.observe(duration)

        logger.info("stock.execute.success", extra={
            "movement_id": movement.id,
            "product_id": movement.product_id,
            "duration": duration,
        })

        return movement

    @staticmethod
    def _lock_product_scope(movement):
        if os.getenv("DISABLE_DB_LOCKS", "true") == "true":
            return

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
            errors_total.labels(type="stock_not_found").inc()
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
                errors_total.labels(type="insufficient_stock").inc()
                raise ValidationError("Stock insuficiente.")

            item.quantity -= movement.quantity
            item.save(update_fields=["quantity"])

    @staticmethod
    def _validate_global_stock(movement, StockItem):
        total = StockItem.objects.filter(
            organization=movement.organization,
            product=movement.product
        ).aggregate(total=Sum("quantity"))["total"] or 0

        if total < 0:
            errors_total.labels(type="global_negative_stock").inc()
            raise ValidationError("Inconsistencia detectada: stock total negativo.")

    @staticmethod
    def _post_commit(movement, user):

        from notifications.events import emit_event
        from notifications.constants import Events
        from inventory.services.stock_alerts import invalidate_dashboard_cache

        emit_event(
            Events.MOVEMENT_CREATED,
            {
                "product": movement.product,
            }
        )

        emit_event(
            Events.STOCK_CHANGED,
            {
                "product": movement.product,
            }
        )

        # 🔥 SOLO invalidamos cache, NO recalculamos todo
        if movement.organization_id:
            invalidate_dashboard_cache(movement.organization_id)