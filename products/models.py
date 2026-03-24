from django.db import models
from django.db.models import Sum
from categories.models import Category
from suppliers.models import Supplier
from django.utils.timezone import now
from django.apps import apps


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

    last_low_stock_alert = models.DateTimeField(null=True, blank=True)

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

    def create_low_stock_notification(self):
        if self.total_stock > self.min_stock:
            return

        Notification = apps.get_model("notifications", "Notification")

        existing = Notification.objects.filter(
            product=self,
            type="stock_low",
            seen=False
        ).first()

        if existing:
            return

        Notification.objects.create(
            product=self,
            type="stock_low",
            message=f"Stock bajo para {self.name}",
            seen=False
        )

        self.last_low_stock_alert = now()
        self.save(update_fields=["last_low_stock_alert"])