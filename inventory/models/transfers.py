from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from products.models import Product
from .locations import Location
from .stock import StockItem
from .movements import StockMovement
from organizations.models import Organization

from inventory.services.audit import (
    audit_transfer_confirmed,
    audit_transfer_cancelled,
)


class StockTransfer(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("received", "Recibida"),
        ("cancelled", "Cancelada"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="transfers",
        db_index=True,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="transfers"
    )

    origin = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transfers_origin"
    )

    destination = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transfers_destination"
    )

    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transfers_created"
    )

    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_confirmed"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self):
        return f"Transferencia #{self.id} - {self.product.name}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        if self.product and self.product.organization_id != self.organization_id:
            raise ValidationError("El producto no pertenece a la organización.")

        if self.origin and self.origin.organization_id != self.organization_id:
            raise ValidationError("El origen no pertenece a la organización.")

        if self.destination and self.destination.organization_id != self.organization_id:
            raise ValidationError("El destino no pertenece a la organización.")

        if not self.origin or not self.destination:
            raise ValidationError("Debe seleccionar origen y destino.")

        if self.origin == self.destination:
            raise ValidationError("El origen y destino no pueden ser iguales.")

        if self.status == "pending":
            stock_item = StockItem.objects.filter(
                organization=self.organization,
                product=self.product,
                location=self.origin
            ).first()

            if not stock_item or stock_item.quantity < self.quantity:
                raise ValidationError("No hay suficiente stock en el almacén de origen.")

    # ==========================================
    # 🔥 BUSINESS ACTIONS (AUDIT CLEAN)
    # ==========================================

    def confirm(self, user):
        if self.status != "pending":
            raise ValidationError("Solo se pueden confirmar transferencias pendientes.")

        old_status = self.status

        StockMovement.objects.create(
            organization=self.organization,
            product=self.product,
            movement_type="TRANSFER",
            origin=self.origin,
            destination=self.destination,
            quantity=self.quantity,
            note=f"Transferencia #{self.id} confirmada",
        )

        self.status = "received"
        self.confirmed_by = user

        from django.utils import timezone
        self.confirmed_at = timezone.now()

        self._skip_audit = True
        self.save()
        del self._skip_audit

        audit_transfer_confirmed(self, user, old_status)

    def cancel(self, user):
        if self.status != "pending":
            raise ValidationError("Solo se pueden cancelar transferencias pendientes.")

        old_status = self.status

        self.status = "cancelled"
        self.confirmed_by = user

        self._skip_audit = True
        self.save()
        del self._skip_audit

        audit_transfer_cancelled(self, user, old_status)

    def save(self, *args, **kwargs):
        if self.product and not self.organization_id:
            self.organization = self.product.organization

        super().save(*args, **kwargs)