from django.db import models
from django.core.exceptions import ValidationError

from products.models import Product
from .locations import Location
from .stock import StockItem


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ("IN", "Entrada"),
        ("OUT", "Salida"),
        ("TRANSFER", "Transferencia"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="movements"
    )
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)

    origin = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_origin"
    )
    destination = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_destination"
    )

    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        if self.movement_type == "TRANSFER":
            if not self.origin or not self.destination:
                raise ValidationError("Las transferencias requieren origen y destino.")
            if self.origin == self.destination:
                raise ValidationError("El origen y destino no pueden ser iguales.")

        if self.movement_type == "IN" and not self.destination:
            raise ValidationError("Las entradas requieren un almacén de destino.")

        if self.movement_type == "OUT":
            if not self.origin:
                raise ValidationError("Las salidas requieren un almacén de origen.")
            stock_item = StockItem.objects.filter(
                product=self.product,
                location=self.origin
            ).first()
            if not stock_item or stock_item.quantity < self.quantity:
                raise ValidationError("No hay suficiente stock en el almacén de origen.")

    def _apply_in(self):
        stock_item, _ = StockItem.objects.get_or_create(
            product=self.product,
            location=self.destination,
            defaults={"quantity": 0},
        )
        stock_item.quantity += self.quantity
        stock_item.save()

    def _apply_out(self):
        stock_item = StockItem.objects.get(
            product=self.product,
            location=self.origin,
        )
        stock_item.quantity -= self.quantity
        stock_item.quantity = max(stock_item.quantity, 0)
        stock_item.save()

    def _apply_transfer(self):
        origin_item = StockItem.objects.get(
            product=self.product,
            location=self.origin,
        )
        origin_item.quantity -= self.quantity
        origin_item.quantity = max(origin_item.quantity, 0)
        origin_item.save()

        dest_item, _ = StockItem.objects.get_or_create(
            product=self.product,
            location=self.destination,
            defaults={"quantity": 0},
        )
        dest_item.quantity += self.quantity
        dest_item.save()

    def apply_to_stock(self):
        if self.movement_type == "IN":
            self._apply_in()
        elif self.movement_type == "OUT":
            self._apply_out()
        elif self.movement_type == "TRANSFER":
            self._apply_transfer()

        # 🔥 NUEVO SISTEMA (events)
        from notifications.events import emit_event
        from inventory.services.stock_alerts import sync_all_notifications

        # 🔥 INVALIDACIÓN CACHE
        from dashboard.services.metrics import invalidate_metrics_cache
        from dashboard.services.charts import invalidate_chart_cache
        from dashboard.services.notifications import invalidate_notifications_cache
        from dashboard.services.activity import invalidate_activity_cache

        invalidate_metrics_cache()
        invalidate_chart_cache()
        invalidate_notifications_cache()
        invalidate_activity_cache()

        # 🔥 EVENTO CENTRALIZADO
        emit_event("movement", {
            "product": self.product,
            "message": f"Movimiento de stock en {self.product.name}",
        })

        sync_all_notifications()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.full_clean()
        super().save(*args, **kwargs)
        if is_new:
            self.apply_to_stock()