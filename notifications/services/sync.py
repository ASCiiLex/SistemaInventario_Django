from django.db.models import F, Sum

from notifications.models import Notification, UserNotification
from notifications.constants import Events


def _stock_item_is_still_low(notification):
    from inventory.models import StockItem

    return StockItem.objects.filter(
        organization=notification.organization,
        product=notification.product,
        location=notification.location,
        quantity__lte=F("min_stock"),
    ).exists()


def _product_is_still_in_risk(notification):
    from inventory.models import StockItem

    agg = (
        StockItem.objects.filter(
            organization=notification.organization,
            product=notification.product,
        ).aggregate(
            total_qty=Sum("quantity"),
            total_min=Sum("min_stock"),
        )
    )

    total_qty = agg["total_qty"] or 0
    total_min = agg["total_min"] or 0

    has_local_issue = StockItem.objects.filter(
        organization=notification.organization,
        product=notification.product,
        quantity__lte=F("min_stock"),
    ).exists()

    return has_local_issue and total_qty <= total_min


def _should_be_active(notification):
    if notification.type == Events.STOCK_LOW:
        return _stock_item_is_still_low(notification)

    if notification.type == Events.PRODUCT_RISK:
        return _product_is_still_in_risk(notification)

    return False


def _get_or_create_notification(org, product, location, notif_type):
    return Notification.objects.get_or_create(
        organization=org,
        product=product,
        location=location,
        type=notif_type,
        defaults={
            "is_active": True,
        },
    )[0]


def _ensure_user_notifications(notification):
    users = UserNotification.objects.filter(
        notification__organization=notification.organization
    ).values_list("user_id", flat=True).distinct()

    if not users:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = User.objects.filter(
            membership__organization=notification.organization
        ).values_list("id", flat=True)

    existing = set(
        UserNotification.objects.filter(notification=notification).values_list(
            "user_id", flat=True
        )
    )

    to_create = []
    for user_id in users:
        if user_id not in existing:
            to_create.append(
                UserNotification(
                    user_id=user_id,
                    notification=notification,
                    seen=False,
                )
            )

    if to_create:
        UserNotification.objects.bulk_create(to_create, ignore_conflicts=True)


def _generate_missing_notifications(organization):
    from inventory.models import StockItem

    stock_items = StockItem.objects.filter(organization=organization)

    for item in stock_items:
        # STOCK LOW
        if item.quantity <= item.min_stock:
            notif = _get_or_create_notification(
                organization,
                item.product,
                item.location,
                Events.STOCK_LOW,
            )
            _ensure_user_notifications(notif)

    # PRODUCT RISK
    products = (
        stock_items.values_list("product_id", flat=True).distinct()
    )

    for product_id in products:
        items = stock_items.filter(product_id=product_id)

        agg = items.aggregate(
            total_qty=Sum("quantity"),
            total_min=Sum("min_stock"),
        )

        total_qty = agg["total_qty"] or 0
        total_min = agg["total_min"] or 0

        has_local_issue = items.filter(
            quantity__lte=F("min_stock")
        ).exists()

        if has_local_issue and total_qty <= total_min:
            sample = items.first()

            notif = _get_or_create_notification(
                organization,
                sample.product,
                sample.location,
                Events.PRODUCT_RISK,
            )
            _ensure_user_notifications(notif)


def sync_notification_state(notification):
    should_be_active = _should_be_active(notification)

    if notification.is_active != should_be_active:
        notification.is_active = should_be_active
        notification.save(update_fields=["is_active"])


def sync_notifications_for_org(organization):
    # 🔥 1. Generar notificaciones si no existen (clave de tu bug)
    _generate_missing_notifications(organization)

    # 🔥 2. Sincronizar estado
    qs = Notification.objects.filter(
        organization=organization,
        type__in=[Events.STOCK_LOW, Events.PRODUCT_RISK],
    )

    for n in qs:
        sync_notification_state(n)