from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from inventory.services.audit import (
    log_action,
    serialize_instance,
    get_instance_changes,
)
from inventory.middleware.audit_user import get_current_user

from notifications.events import emit_event
from notifications.constants import Events

from inventory.models.stock import StockItem
from inventory.models.orders import Order, OrderItem
from inventory.models.transfers import StockTransfer
from inventory.models.locations import Location
from inventory.models.movements import StockMovement
from products.models import Product


AUDITED_MODELS = [
    StockItem,
    Order,
    OrderItem,
    StockTransfer,
    Location,
    StockMovement,
    Product,
]


@receiver(pre_save)
def store_old_instance(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    if getattr(instance, "_skip_audit", False):
        return

    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._audit_old_data = serialize_instance(old)
        except sender.DoesNotExist:
            instance._audit_old_data = {}
    else:
        instance._audit_old_data = {}


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    if getattr(instance, "_skip_audit", False):
        return

    user = get_current_user()

    if created:
        log_action(
            user=user,
            action="CREATE",
            instance=instance,
            changes=serialize_instance(instance),
        )

        # 🔥 SOLO EVENTOS REALES
        if isinstance(instance, StockItem):
            emit_event(Events.STOCK_CHANGED, {"instance": instance})

        if isinstance(instance, Order):
            emit_event(Events.ORDERS_UPDATED, {"instance": instance})

        return

    old_data = getattr(instance, "_audit_old_data", {})
    changes = get_instance_changes(old_data, instance)

    if changes:
        log_action(
            user=user,
            action="UPDATE",
            instance=instance,
            changes=changes,
        )

        if isinstance(instance, StockItem):
            emit_event(Events.STOCK_CHANGED, {"instance": instance})

        if isinstance(instance, Order):
            emit_event(Events.ORDERS_UPDATED, {"instance": instance})


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    if getattr(instance, "_skip_audit", False):
        return

    user = get_current_user()

    log_action(
        user=user,
        action="DELETE",
        instance=instance,
        changes=serialize_instance(instance),
    )