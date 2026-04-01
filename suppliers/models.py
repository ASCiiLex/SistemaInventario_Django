from django.db import models
from organizations.models import Organization


class Supplier(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="suppliers",
        db_index=True,
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=150, db_index=True)
    contact_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    lead_time_days = models.PositiveIntegerField(default=0)
    default_order_quantity = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=["organization", "name"]),
        ]

    def __str__(self):
        return self.name