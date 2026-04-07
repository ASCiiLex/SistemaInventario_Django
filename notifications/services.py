from django.utils import timezone
from datetime import timedelta

from .models import Notification, UserNotification
from .utils import send_to_user
from .events import register_event
from .preferences import is_event_enabled

from organizations.models import Membership


COOLDOWNS = {
    "stock_item_low": 30,
    "product_risk": 60,
}


PRIORITY_MAP = {
    "stock_item_low": "critical",
    "product_risk": "warning",
    "movement": "info",
    "order": "info",
}


def _get_priority(type_):
    return PRIORITY_MAP.get(type_, "info")


def _resolve_organization(product=None, location=None):
    if product and hasattr(product, "organization_id"):
        return product.organization
    if location and hasattr(location, "organization_id"):
        return location.organization
    return None


def _is_duplicate(organization, product=None, location=None, type_=None):
    minutes = COOLDOWNS.get(type_, 30)
    since = timezone.now() - timedelta(minutes=minutes)

    qs = Notification.objects.filter(
        organization=organization,
        type=type_,
        created_at__gte=since
    )

    if product:
        qs = qs.filter(product=product)

    if location:
        qs = qs.filter(location=location)

    return qs.exists()


def _get_target_users(organization):
    from .preferences import ensure_user_preferences

    memberships = (
        Membership.objects
        .select_related("user")
        .filter(organization=organization, is_active=True)
    )

    users = [m.user for m in memberships]

    for user in users:
        ensure_user_preferences(user)

    return users


def create_notification(*, product=None, location=None, type_, message):
    organization = _resolve_organization(product, location)

    if not organization:
        return None

    if _is_duplicate(organization, product=product, location=location, type_=type_):
        return None

    notification = Notification.objects.create(
        organization=organization,
        product=product,
        location=location,
        type=type_,
        priority=_get_priority(type_),
        message=message,
    )

    users = _get_target_users(organization)

    user_notifications = []

    for user in users:
        if not is_event_enabled(user, type_):
            continue

        user_notifications.append(
            UserNotification(
                user=user,
                notification=notification,
                seen=False,
            )
        )

        send_to_user(
            user.id,
            {
                "event": type_,
                "type": "notification",  # compatibilidad frontend
                "message": message,
                "product": product.id if product else None,
            }
        )

    UserNotification.objects.bulk_create(user_notifications, ignore_conflicts=True)

    return notification


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