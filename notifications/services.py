from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

from .models import Notification, UserNotification
from .utils import send_to_user, send_ui_event_to_all
from .events import register_event
from .preferences import is_event_enabled
from .constants import Events

from organizations.models import Membership


COOLDOWNS = {
    Events.STOCK_LOW: 30,
    Events.PRODUCT_RISK: 60,
}


PRIORITY_MAP = {
    Events.STOCK_LOW: "warning",
    Events.PRODUCT_RISK: "critical",
    Events.MOVEMENT_CREATED: "info",
    Events.ORDERS_UPDATED: "info",
}


MESSAGE_TEMPLATES = {
    Events.STOCK_LOW: lambda p, l: f"Stock bajo en {l.name}: {p.name}",
    Events.PRODUCT_RISK: lambda p, l: f"Producto en riesgo: {p.name}",
    Events.MOVEMENT_CREATED: lambda p, l: f"Movimiento de stock: {p.name}",
    Events.ORDERS_UPDATED: lambda p, l: "Actualización de pedidos",
}


def _invalidate_user_cache(user_id, org_id):
    cache.delete(f"notifications:unread_count:{user_id}:{org_id}")
    cache.delete(f"dashboard:notifications:{user_id}:{org_id}:summary")
    cache.delete_pattern(f"dashboard:notifications:{user_id}:{org_id}:recent*")


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
        created_at__gte=since,
    )

    if type_ == Events.PRODUCT_RISK:
        qs = qs.filter(product=product)
    else:
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


def _build_message(type_, product=None, location=None):
    template = MESSAGE_TEMPLATES.get(type_)
    return template(product, location) if template else type_


def create_notification(*, product=None, location=None, type_):
    organization = _resolve_organization(product, location)

    if not organization:
        return None

    if _is_duplicate(organization, product=product, location=location, type_=type_):
        return None

    message = _build_message(type_, product, location)

    notification = Notification.objects.create(
        organization=organization,
        product=product,
        location=location,
        type=type_,
        priority=_get_priority(type_),
        message=message,
    )

    users = _get_target_users(organization)

    bulk = []

    for user in users:
        if not is_event_enabled(user, type_):
            continue

        bulk.append(
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
                "message": message,
                "priority": notification.priority,
            }
        )

        _invalidate_user_cache(user.id, organization.id)

    UserNotification.objects.bulk_create(bulk, ignore_conflicts=True)

    send_ui_event_to_all({
        "event": Events.NOTIFICATIONS_UPDATED
    })

    return notification


@register_event(Events.STOCK_LOW)
def handle_stock_low(payload: dict):
    create_notification(
        product=payload.get("product"),
        location=payload.get("location"),
        type_=Events.STOCK_LOW,
    )


@register_event(Events.PRODUCT_RISK)
def handle_product_risk(payload: dict):
    create_notification(
        product=payload.get("product"),
        type_=Events.PRODUCT_RISK,
    )