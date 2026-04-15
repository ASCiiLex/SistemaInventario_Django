from django.db import models
from organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


class ImportJob(models.Model):

    STATUS_CHOICES = (
        ("preview", "Preview"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="import_jobs",
        db_index=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_jobs",
    )

    file_name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="preview",
        db_index=True,
    )

    total_rows = models.PositiveIntegerField(default=0)
    valid_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self):
        return f"ImportJob #{self.id} ({self.status})"