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