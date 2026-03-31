from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from products.models import Product
from inventory.models import Location


class Notification(models.Model):

    TYPE_CHOICES = [
        ("movement", "Movimiento"),
        ("stock_item_low", "Incidencia almacén"),
        ("product_risk", "Producto en riesgo"),
        ("order", "Pedido"),
        ("alert", "Alerta"),
        ("info", "Información"),
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
        max_length=30,
        choices=TYPE_CHOICES,
        default="info",
        db_index=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="info",
    )

    message = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # ⚠️ deprecated (se mantiene para compatibilidad)
    seen = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["seen", "-created_at"]),
            models.Index(fields=["type", "-created_at"]),
            models.Index(fields=["product", "type"]),
            models.Index(fields=["location", "type"]),
        ]

    def __str__(self):
        return self.message

    @classmethod
    def recently_created(cls, *, product=None, location=None, type=None, minutes=30):
        since = timezone.now() - timedelta(minutes=minutes)

        qs = cls.objects.filter(
            type=type,
            created_at__gte=since
        )

        if product:
            qs = qs.filter(product=product)

        if location:
            qs = qs.filter(location=location)

        return qs.exists()


# =========================
# NUEVO MODELO (CLAVE SaaS)
# =========================

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
            models.Index(fields=["notification", "user"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.notification}"