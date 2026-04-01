from django.db import models
from organizations.models import Organization


class Category(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="categories",
        db_index=True,
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=["organization", "name"]),
        ]

    def __str__(self):
        return self.name