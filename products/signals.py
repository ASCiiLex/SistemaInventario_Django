from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from notifications.models import Notification

@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    if instance.stock <= instance.min_stock:
        Notification.objects.create(
            product=instance,
            message=f"Stock bajo para {instance.name}",
            seen=False
        )