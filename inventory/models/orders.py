from django.db import models
from suppliers.models import Supplier
from products.models import Product
from .locations import Location
from organizations.models import Organization

from inventory.services.audit import (
    audit_order_sent,
    audit_order_received,
    audit_order_cancelled,
)


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("sent", "Enviado"),
        ("received", "Recibido"),
        ("cancelled", "Cancelado"),
        ("partially_received", "Parcialmente recibido"),
        ("backordered", "Backorder"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="orders",
        db_index=True,
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

    estimated_arrival = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.supplier.name if self.supplier else 'N/A'}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_cost(self):
        return sum(item.total_cost for item in self.items.all())

    # ==========================================
    # 🔥 BUSINESS ACTIONS (AUDIT CLEAN)
    # ==========================================

    def mark_as_sent(self, user):
        if self.status != "pending":
            return

        old_status = self.status

        from django.utils import timezone
        self.status = "sent"
        self.sent_at = timezone.now()

        self._skip_audit = True
        self.save()
        del self._skip_audit

        audit_order_sent(self, user, old_status)

    def mark_as_received(self, user):
        if self.status not in ["sent", "partially_received", "backordered"]:
            return

        old_status = self.status

        from django.utils import timezone
        self.status = "received"
        self.received_at = timezone.now()

        self._skip_audit = True
        self.save()
        del self._skip_audit

        audit_order_received(self, user, old_status)

    def mark_as_cancelled(self, user):
        if self.status in ["received", "cancelled"]:
            return

        old_status = self.status

        self.status = "cancelled"

        self._skip_audit = True
        self.save()
        del self._skip_audit

        audit_order_cancelled(self, user, old_status)


class OrderItem(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="order_items",
        db_index=True,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "order"]),
        ]

    def __str__(self):
        return f"{self.product.name if self.product else 'N/A'} x {self.quantity}"

    @property
    def total_cost(self):
        return self.quantity * self.cost_price

    def save(self, *args, **kwargs):
        if self.order and not self.organization_id:
            self.organization = self.order.organization
        super().save(*args, **kwargs)