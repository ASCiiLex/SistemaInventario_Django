from django.db import models
from django.core.exceptions import ValidationError
from products.models import Product

class Movement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def clean(self):
        if self.movement_type == 'OUT' and self.quantity > self.product.stock:
            raise ValidationError("No hay suficiente stock para realizar esta salida.")

    class Meta:
        ordering = ['-created_at']