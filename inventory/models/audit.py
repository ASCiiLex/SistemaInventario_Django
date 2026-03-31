from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("STATUS_CHANGE", "Status change"),
        ("IMPORT", "Import"),
        ("OTHER", "Other"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()

    changes = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.model_name} ({self.object_id})"