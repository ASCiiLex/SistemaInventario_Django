from django.db import models
from django.core.exceptions import ValidationError
from suppliers.models import Supplier
from products.models import Product


class Location(models.Model):
    name = models.CharField(max_length=150, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return self.name


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

    class Meta:
        unique_together = ("product", "location")
        verbose_name = "Stock Item"
        verbose_name_plural = "Stock Items"

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity}"

    @property
    def is_below_minimum(self):
        return self.quantity <= self.product.min_stock


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ("IN", "Entrada"),
        ("OUT", "Salida"),
        ("TRANSFER", "Transferencia"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)

    origin = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_origin"
    )
    destination = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_destination"
    )

    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def clean(self):
        if self.movement_type == "TRANSFER":
            if not self.origin or not self.destination:
                raise ValidationError("Las transferencias requieren origen y destino.")
            if self.origin == self.destination:
                raise ValidationError("El origen y destino no pueden ser iguales.")

        if self.movement_type == "OUT":
            stock_item = StockItem.objects.filter(
                product=self.product,
                location=self.origin
            ).first()
            if not stock_item or stock_item.quantity < self.quantity:
                raise ValidationError("No hay suficiente stock en el almacén de origen.")


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