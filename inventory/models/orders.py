from django.db import models, transaction
from django.core.exceptions import ValidationError

from suppliers.models import Supplier
from products.models import Product
from .locations import Location
from organizations.models import Organization

from inventory.services.audit import (
    audit_order_sent,
    audit_order_received,
    audit_order_cancelled,
)

from inventory.models.movements import StockMovement


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
    def total_received(self):
        """
        🔥 Total realmente recibido vía movimientos (source of truth real)
        """
        return sum(
            StockMovement.objects.filter(
                organization=self.organization,
                movement_type="IN",
                destination=self.location,
                note__startswith=f"order:{self.id}"
            ).values_list("quantity", flat=True)
        )

    # ==========================================
    # 🔥 BUSINESS ACTIONS (STRICT)
    # ==========================================

    def mark_as_sent(self, user):
        if self.status != "pending":
            raise ValidationError("Solo pedidos pendientes pueden enviarse.")

        from django.utils import timezone

        old_status = self.status
        self.status = "sent"
        self.sent_at = timezone.now()

        self._skip_audit = True
        self.save(update_fields=["status", "sent_at"])
        del self._skip_audit

        audit_order_sent(self, user, old_status)

    def receive_items(self, user, items_data):
        """
        🔥 RECEPCIÓN REAL → CREA MOVIMIENTOS
        items_data = [{product, quantity}]
        """

        if self.status not in ["sent", "partially_received", "backordered"]:
            raise ValidationError("Pedido no receivable.")

        if not self.location:
            raise ValidationError("Pedido sin ubicación.")

        with transaction.atomic():

            for item_data in items_data:
                product = item_data["product"]
                qty = item_data["quantity"]

                order_item = self.items.filter(product=product).first()
                if not order_item:
                    raise ValidationError("Producto no pertenece al pedido.")

                if qty <= 0:
                    raise ValidationError("Cantidad inválida.")

                # 🔒 CREAR MOVIMIENTO REAL
                movement = StockMovement(
                    organization=self.organization,
                    product=product,
                    movement_type="IN",
                    destination=self.location,
                    quantity=qty,
                    note=f"order:{self.id}:{product.id}",
                    idempotency_key=f"order:{self.id}:{product.id}"
                )
                movement.save()

            # 🔥 REEVALUAR ESTADO
            total_expected = sum(i.quantity for i in self.items.all())
            total_received = self.total_received

            old_status = self.status

            if total_received == 0:
                self.status = "sent"
            elif total_received < total_expected:
                self.status = "partially_received"
            else:
                self.status = "received"

                from django.utils import timezone
                self.received_at = timezone.now()

            self._skip_audit = True
            self.save(update_fields=["status", "received_at"])
            del self._skip_audit

        audit_order_received(self, user, old_status)

    def mark_as_cancelled(self, user):
        if self.status in ["received", "cancelled"]:
            raise ValidationError("No se puede cancelar.")

        old_status = self.status

        self.status = "cancelled"

        self._skip_audit = True
        self.save(update_fields=["status"])
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