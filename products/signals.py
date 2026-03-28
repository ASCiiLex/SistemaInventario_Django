from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from notifications.models import Notification
from notifications.utils import broadcast_notification


@receiver(post_save, sender=Product)
def check_product_risk(sender, instance, **kwargs):
    if not instance.is_below_minimum:
        return

    exists = Notification.objects.filter(
        product=instance,
        type="product_risk",
        seen=False
    ).exists()

    if exists:
        return

    Notification.objects.create(
        product=instance,
        type="product_risk",
        message=f"Producto en riesgo: {instance.name}",
    )

    broadcast_notification({
        "type": "product_risk",
        "message": f"Producto en riesgo: {instance.name}",
        "product": instance.name,
    })