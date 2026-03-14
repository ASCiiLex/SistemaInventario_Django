from django.db import models
from products.models import Product


class Notification(models.Model):

    TYPE_CHOICES = [
        ("movement", "Movimiento"),
        ("stock_low", "Stock bajo"),
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

    type = models.CharField(
        max_length=20,
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