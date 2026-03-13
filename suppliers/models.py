from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    contact_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    lead_time_days = models.PositiveIntegerField(default=0)
    default_order_quantity = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name