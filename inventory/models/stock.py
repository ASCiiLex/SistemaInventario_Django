from django.db import models
from django.core.exceptions import ValidationError

from products.models import Product
from .locations import Location
from organizations.models import Organization


class StockItem(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="stock_items",
        db_index=True,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_items",
        db_index=True,
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="stock_items",
        db_index=True,
    )

    quantity = models.PositiveIntegerField(default=0, db_index=True)
    min_stock = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        unique_together = ("organization", "product", "location")
        indexes = [
            models.Index(fields=["organization", "product"]),
            models.Index(fields=["organization", "location"]),
        ]

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity}"

    def clean(self):
        if self.quantity < 0:
            raise ValidationError("El stock no puede ser negativo.")

        if self.min_stock < 0:
            raise ValidationError("El mínimo no puede ser negativo.")

    @property
    def is_below_minimum(self):
        return self.quantity <= self.min_stock