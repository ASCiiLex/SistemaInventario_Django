from django.db import models
from django.core.exceptions import ValidationError
from django.apps import apps

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
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"

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

        Notification = apps.get_model("notifications", "Notification")

        # 🔥 INCIDENCIAS POR ALMACÉN
        affected_items = StockItem.objects.filter(product=self.product)

        for item in affected_items:
            if item.quantity <= item.min_stock:

                exists = Notification.objects.filter(
                    product=self.product,
                    location=item.location,
                    type="stock_item_low",
                    seen=False
                ).exists()

                if not exists:
                    Notification.objects.create(
                        product=self.product,
                        location=item.location,
                        type="stock_item_low",
                        message=f"{self.product.name} bajo mínimo en {item.location.name}",
                    )

                    from notifications.utils import broadcast_notification
                    broadcast_notification({
                        "type": "stock_item_low",
                        "message": f"{self.product.name} bajo mínimo en {item.location.name}",
                        "product": self.product.name,
                    })

        # 🔥 PRODUCTO GLOBAL
        self.product.create_low_stock_notification()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.full_clean()
        super().save(*args, **kwargs)
        if is_new:
            self.apply_to_stock()