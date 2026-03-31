from django.db import models
from products.models import Product
from .locations import Location


class StockItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_items"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="stock_items"
    )
    quantity = models.PositiveIntegerField(default=0)

    min_stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "location")
        verbose_name = "Stock Item"
        verbose_name_plural = "Stock Items"

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity}"

    @property
    def is_below_minimum(self):
        return self.quantity <= self.min_stock