from django.db.models import F, Sum
from notifications.models import Notification
from notifications.constants import Events


def _stock_item_is_still_low(notification):
    from inventory.models import StockItem

    return StockItem.objects.filter(
        organization=notification.organization,
        product=notification.product,
        location=notification.location,
        quantity__lte=F("min_stock")
    ).exists()


def _product_is_still_in_risk(notification):
    from inventory.models import StockItem

    agg = (
        StockItem.objects
        .filter(organization=notification.organization, product=notification.product)
        .aggregate(
            total_qty=Sum("quantity"),
            total_min=Sum("min_stock"),
        )
    )

    total_qty = agg["total_qty"] or 0
    total_min = agg["total_min"] or 0

    has_local_issue = StockItem.objects.filter(
        organization=notification.organization,
        product=notification.product,
        quantity__lte=F("min_stock")
    ).exists()

    return has_local_issue and total_qty <= total_min


def _should_be_active(notification):
    if notification.type == Events.STOCK_LOW:
        return _stock_item_is_still_low(notification)

    if notification.type == Events.PRODUCT_RISK:
        return _product_is_still_in_risk(notification)

    return False


def sync_notification_state(notification):
    should_be_active = _should_be_active(notification)

    if notification.is_active != should_be_active:
        notification.is_active = should_be_active
        notification.save(update_fields=["is_active"])


def sync_notifications_for_org(organization):
    qs = Notification.objects.filter(
        organization=organization,
        type__in=[Events.STOCK_LOW, Events.PRODUCT_RISK]
    )

    for n in qs:
        sync_notification_state(n)