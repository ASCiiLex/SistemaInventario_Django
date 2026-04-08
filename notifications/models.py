from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from organizations.models import Organization
from products.models import Product
from inventory.models import Location

from notifications.constants import Events


class Notification(models.Model):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )

    TYPE_CHOICES = [
        (Events.MOVEMENT_CREATED, "Movimiento"),
        (Events.STOCK_LOW, "Stock bajo"),
        (Events.PRODUCT_RISK, "Producto en riesgo"),
        (Events.ORDERS_UPDATED, "Pedido"),
    ]

    PRIORITY_CHOICES = [
        ("critical", "Crítica"),
        ("warning", "Advertencia"),
        ("info", "Info"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        db_index=True,
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        db_index=True,
    )

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        db_index=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="info",
    )

    message = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # 🔥 CONSISTENCIA CON DB
    seen = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["organization", "type"]),
        ]

    def __str__(self):
        return self.message

    @classmethod
    def recently_created(cls, *, organization, product=None, location=None, type=None, minutes=30):
        since = timezone.now() - timedelta(minutes=minutes)

        qs = cls.objects.filter(
            organization=organization,
            type=type,
            created_at__gte=since
        )

        if product:
            qs = qs.filter(product=product)

        if location:
            qs = qs.filter(location=location)

        return qs.exists()


class UserNotification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_notifications"
    )

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="user_notifications"
    )

    seen = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "notification")
        indexes = [
            models.Index(fields=["user", "seen"]),
        ]