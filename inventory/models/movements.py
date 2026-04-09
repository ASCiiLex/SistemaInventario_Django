from django.db import models
from django.core.exceptions import ValidationError

from products.models import Product
from .locations import Location
from organizations.models import Organization

from inventory.services.stock_domain import StockDomainService


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ("IN", "Entrada"),
        ("OUT", "Salida"),
        ("TRANSFER", "Transferencia"),
    )

    SOURCE_TYPES = (
        ("manual", "Manual"),
        ("order", "Pedido"),
        ("transfer", "Transferencia"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="movements",
        db_index=True,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        default="manual",
        db_index=True,
    )

    order = models.ForeignKey(
        "inventory.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )

    transfer = models.ForeignKey(
        "inventory.StockTransfer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )

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

    idempotency_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "idempotency_key"],
                name="unique_movement_idempotency_per_org",
                condition=~models.Q(idempotency_key=None)
            )
        ]
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["organization", "idempotency_key"]),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        if self.product and self.product.organization_id != self.organization_id:
            raise ValidationError("El producto no pertenece a la organización.")

        if self.origin and self.origin.organization_id != self.organization_id:
            raise ValidationError("El origen no pertenece a la organización.")

        if self.destination and self.destination.organization_id != self.organization_id:
            raise ValidationError("El destino no pertenece a la organización.")

        # 🔥 BLOQUEO: manual no puede ser TRANSFER
        if self.source_type == "manual" and self.movement_type == "TRANSFER":
            raise ValidationError("Las transferencias no pueden crearse manualmente.")

        if self.source_type == "order" and not self.order:
            raise ValidationError("Movimiento de pedido sin order.")

        if self.source_type == "transfer" and not self.transfer:
            raise ValidationError("Movimiento de transferencia sin transfer.")

        if self.source_type == "manual" and (self.order or self.transfer):
            raise ValidationError("Movimiento manual no puede tener relaciones.")

        if self.movement_type == "IN" and not self.destination:
            raise ValidationError("Las entradas requieren destino.")

        if self.movement_type == "OUT" and not self.origin:
            raise ValidationError("Las salidas requieren origen.")

    def save(self, *args, **kwargs):
        if self.product and not self.organization_id:
            self.organization = self.product.organization

        is_new = self.pk is None

        if is_new:
            return StockDomainService.execute(self)

        return super().save(*args, **kwargs)