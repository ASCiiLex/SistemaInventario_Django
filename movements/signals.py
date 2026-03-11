from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Movement


@receiver(pre_save, sender=Movement)
def adjust_stock_on_edit(sender, instance, **kwargs):
    if not instance.pk:
        return  # Es una creación, no una edición

    old = Movement.objects.get(pk=instance.pk)
    product = instance.product

    # Revertir el movimiento anterior
    if old.movement_type == 'IN':
        product.stock -= old.quantity
    else:
        product.stock += old.quantity

    # Aplicar el nuevo movimiento
    if instance.movement_type == 'IN':
        product.stock += instance.quantity
    else:
        product.stock -= instance.quantity

    product.save()


@receiver(post_save, sender=Movement)
def adjust_stock_on_create(sender, instance, created, **kwargs):
    if not created:
        return

    product = instance.product

    if instance.movement_type == 'IN':
        product.stock += instance.quantity
    else:
        product.stock -= instance.quantity

    product.save()


@receiver(pre_delete, sender=Movement)
def adjust_stock_on_delete(sender, instance, **kwargs):
    product = instance.product

    if instance.movement_type == 'IN':
        product.stock -= instance.quantity
    else:
        product.stock += instance.quantity

    product.save()