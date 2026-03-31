from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from .models import Notification
from .utils import send_to_user
from .events import register_event
from .preferences import is_event_enabled


COOLDOWNS = {
    "stock_item_low": 30,
    "product_risk": 60,
}


PRIORITY_MAP = {
    "stock_item_low": "critical",
    "product_risk": "warning",
    "movement": "info",
    "order": "info",
    "alert": "warning",
    "info": "info",
}


ICON_MAP = {
    "critical": "🔴",
    "warning": "⚠️",
    "info": "🔔",
}


def _get_priority(type_):
    return PRIORITY_MAP.get(type_, "info")


def _is_duplicate(product=None, location=None, type_=None):
    minutes = COOLDOWNS.get(type_, 30)

    since = timezone.now() - timedelta(minutes=minutes)

    qs = Notification.objects.filter(
        type=type_,
        created_at__gte=since
    )

    if product:
        qs = qs.filter(product=product)

    if location:
        qs = qs.filter(location=location)

    return qs.exists()


def _get_target_users(event_type: str):
    return User.objects.prefetch_related("notification_preferences")


def create_notification(*, product=None, location=None, type_, message):
    if _is_duplicate(product=product, location=location, type_=type_):
        return None

    notification = Notification.objects.create(
        product=product,
        location=location,
        type=type_,
        priority=_get_priority(type_),
        message=message,
    )

    users = _get_target_users(type_)

    for user in users:
        if not is_event_enabled(user, type_):
            continue

        send_to_user(
            user.id,
            {
                "type": "notification",
                "message": message,
                "product": product.id if product else None,
            }
        )

    return notification


# =========================
# EVENT HANDLERS
# =========================

@register_event("stock_item_low")
def handle_stock_item_low(payload: dict):
    create_notification(
        product=payload.get("product"),
        location=payload.get("location"),
        type_="stock_item_low",
        message=payload.get("message"),
    )


@register_event("product_risk")
def handle_product_risk(payload: dict):
    create_notification(
        product=payload.get("product"),
        type_="product_risk",
        message=payload.get("message"),
    )


@register_event("order_created")
def handle_order_created(payload: dict):
    create_notification(
        type_="order",
        message=payload.get("message"),
    )


def get_grouped_notifications(notifications):
    grouped = {}

    for n in notifications:
        key = n.product_id or "no-product"

        if key not in grouped:
            grouped[key] = {
                "product": n.product,
                "count": 0,
                "items": [],
                "icons": set(),
            }

        grouped[key]["count"] += 1
        grouped[key]["items"].append(n)

        icon = ICON_MAP.get(n.priority, "🔔")
        grouped[key]["icons"].add(icon)

    for g in grouped.values():
        g["items"].sort(key=lambda x: x.created_at, reverse=True)
        g["icons"] = list(g["icons"])

    return list(grouped.values())