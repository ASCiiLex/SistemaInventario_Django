from django.db import models
from categories.models import Category
from suppliers.models import Supplier

def product_image_path(instance, filename):
    return f'products/{instance.sku}/{filename}'

class Product(models.Model):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='products')
    stock = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_below_minimum(self):
        return self.stock <= self.min_stock