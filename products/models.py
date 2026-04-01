from django.db import models
from django.db.models import Sum
from categories.models import Category
from suppliers.models import Supplier
from django.utils.timezone import now
from django.apps import apps
from organizations.models import Organization


def product_image_path(instance, filename):
    return f'products/{instance.sku}/{filename}'


class Product(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True,
    )

    name = models.CharField(max_length=150, db_index=True)
    sku = models.CharField(max_length=50, db_index=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    stock = models.IntegerField(default=0)

    min_stock = models.IntegerField(default=0)

    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    image = models.ImageField(upload_to=product_image_path, blank=True, null=True)

    last_low_stock_alert = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ("organization", "sku")
        indexes = [
            models.Index(fields=["organization", "name"]),
            models.Index(fields=["organization", "sku"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def total_stock(self):
        total = self.stock_items.aggregate(total=Sum("quantity"))["total"]
        return total or 0

    @property
    def total_min_stock(self):
        total = self.stock_items.aggregate(total=Sum("min_stock"))["total"]
        return total or 0

    @property
    def is_below_minimum(self):
        return self.total_stock <= self.total_min_stock

    @property
    def margin(self):
        return self.sale_price - self.cost_price

    @property
    def inventory_value(self):
        return self.total_stock * self.cost_price