from django.db import models
from django.db.models import Sum
from categories.models import Category
from suppliers.models import Supplier


def product_image_path(instance, filename):
    return f'products/{instance.sku}/{filename}'


class Product(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    sku = models.CharField(max_length=50, unique=True, db_index=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def total_stock(self):
        if hasattr(self, "stock_items"):
            total = self.stock_items.aggregate(total=Sum("quantity"))["total"]
            if total is not None:
                return total
        return self.stock

    @property
    def is_below_minimum(self):
        return self.total_stock <= self.min_stock

    @property
    def margin(self):
        return self.sale_price - self.cost_price

    @property
    def inventory_value(self):
        return self.total_stock * self.cost_price

    @property
    def total_in(self):
        return self.movements.filter(movement_type='IN').aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    @property
    def total_out(self):
        return self.movements.filter(movement_type='OUT').aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    @property
    def last_movement(self):
        return self.movements.order_by('-created_at').first()