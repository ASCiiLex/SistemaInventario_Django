from django.db import models
from categories.models import Category
from suppliers.models import Supplier
from notifications.models import Notification


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
    def is_below_minimum(self):
        return self.stock <= self.min_stock

    @property
    def total_in(self):
        return self.movements.filter(movement_type='IN').aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    @property
    def total_out(self):
        return self.movements.filter(movement_type='OUT').aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    @property
    def last_movement(self):
        return self.movements.order_by('-created_at').first()

    def create_low_stock_notification(self):
        if self.is_below_minimum:
            Notification.objects.create(
                product=self,
                message=f"El producto {self.name} está por debajo del stock mínimo."
            )