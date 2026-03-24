from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from notifications.utils import broadcast_notification


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    before = instance.last_low_stock_alert
    instance.create_low_stock_notification()
    after = instance.last_low_stock_alert

    if before != after:
        broadcast_notification({
            "type": "stock_low",
            "message": f"Stock bajo para {instance.name}",
            "product": instance.name,
        })