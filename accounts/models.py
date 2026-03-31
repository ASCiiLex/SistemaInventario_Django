from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        STAFF = "STAFF", "Staff"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STAFF)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class UserNotificationPreference(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    event_type = models.CharField(max_length=50)

    enabled = models.BooleanField(default=True)

    email_enabled = models.BooleanField(default=False)  # 🔜 futuro

    class Meta:
        unique_together = ("user", "event_type")
        indexes = [
            models.Index(fields=["user", "event_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event_type} ({'ON' if self.enabled else 'OFF'})"