from django.db import models
from products.models import Product
from .locations import Location


class StockItem(models.Model):
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
        unique_together = ("product", "location")
        indexes = [
            models.Index(fields=["product", "location"]),
            models.Index(fields=["quantity", "min_stock"]),
            models.Index(fields=["product", "quantity"]),
        ]

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity}"

    @property
    def is_below_minimum(self):
        return self.quantity <= self.min_stock