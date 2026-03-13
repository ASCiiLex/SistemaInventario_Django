from django.db import models
from suppliers.models import Supplier
from products.models import Product
from .locations import Location

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("sent", "Enviado"),
        ("received", "Recibido"),
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

    estimated_arrival = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.id} - {self.supplier.name if self.supplier else 'N/A'}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_cost(self):
        return sum(item.total_cost for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_cost(self):
        return self.quantity * self.cost_price