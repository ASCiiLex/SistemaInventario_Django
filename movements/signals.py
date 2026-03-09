from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movement

@receiver(post_save, sender=Movement)
def update_stock(sender, instance, created, **kwargs):
    if not created:
        return

    product = instance.product

    if instance.movement_type == 'IN':
        product.stock += instance.quantity
    elif instance.movement_type == 'OUT':
        product.stock -= instance.quantity

    product.save()