from django.db import models
from products.models import Product
from inventory.models import Location


class Notification(models.Model):

    TYPE_CHOICES = [
        ("movement", "Movimiento"),
        ("stock_item_low", "Incidencia almacén"),
        ("product_risk", "Producto en riesgo"),
        ("order", "Pedido"),
        ("alert", "Alerta"),
        ("info", "Información"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default="info"
    )

    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message