from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from products.models import Product
from .locations import Location
from .movements import StockMovement
from organizations.models import Organization

from inventory.services.audit import (
    audit_transfer_confirmed,
    audit_transfer_cancelled,
)


class StockTransfer(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("in_transit", "En tránsito"),
        ("completed", "Completada"),
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

    idempotency_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

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
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "idempotency_key"],
                name="unique_transfer_idempotency_per_org",
                condition=~models.Q(idempotency_key=None)
            )
        ]

    def __str__(self):
        return f"Transfer #{self.id} - {self.product.name}"

    # ==========================================
    # 🔥 CONFIRM → SALE DE ORIGEN (IN TRANSIT)
    # ==========================================
    def confirm(self, user):

        if self.status != "pending":
            return self

        old_status = self.status

        with transaction.atomic():

            locked = StockTransfer.objects.select_for_update().get(pk=self.pk)

            if locked.status != "pending":
                return locked

            # 🔥 MOVIMIENTO OUT
            movement = StockMovement(
                organization=self.organization,
                product=self.product,
                movement_type="OUT",
                source_type="transfer",
                transfer=self,
                origin=self.origin,
                quantity=self.quantity,
                idempotency_key=f"transfer:{self.id}:out"
            )

            movement.save()

            locked.status = "in_transit"
            locked.confirmed_by = user
            locked.confirmed_at = timezone.now()

            locked._skip_audit = True
            locked.save(update_fields=["status", "confirmed_by", "confirmed_at"])
            del locked._skip_audit

        audit_transfer_confirmed(self, user, old_status)

        return self

    # ==========================================
    # 🔥 COMPLETE → LLEGA A DESTINO
    # ==========================================
    def complete(self, user):

        if self.status != "in_transit":
            raise ValidationError("La transferencia no está en tránsito.")

        with transaction.atomic():

            locked = StockTransfer.objects.select_for_update().get(pk=self.pk)

            if locked.status != "in_transit":
                return locked

            movement = StockMovement(
                organization=self.organization,
                product=self.product,
                movement_type="IN",
                source_type="transfer",
                transfer=self,
                destination=self.destination,
                quantity=self.quantity,
                idempotency_key=f"transfer:{self.id}:in"
            )

            movement.save()

            locked.status = "completed"
            locked.completed_at = timezone.now()

            locked._skip_audit = True
            locked.save(update_fields=["status", "completed_at"])
            del locked._skip_audit

        return self

    # ==========================================
    # 🔥 CANCEL
    # ==========================================
    def cancel(self, user):

        if self.status != "pending":
            raise ValidationError("Solo transferencias pendientes pueden cancelarse.")

        old_status = self.status

        self.status = "cancelled"
        self.confirmed_by = user

        self._skip_audit = True
        self.save(update_fields=["status", "confirmed_by"])
        del self._skip_audit

        audit_transfer_cancelled(self, user, old_status)

        return self

    def save(self, *args, **kwargs):
        if self.product and not self.organization_id:
            self.organization = self.product.organization

        super().save(*args, **kwargs)