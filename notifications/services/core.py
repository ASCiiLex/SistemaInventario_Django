from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

from notifications.models import Notification, UserNotification
from notifications.utils import send_to_user, send_ui_event_to_all
from notifications.preferences import is_event_enabled
from notifications.constants import Events

from organizations.models import Membership


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


def _safe_delete_pattern(pattern):
    try:
        cache.delete_pattern(pattern)
    except AttributeError:
        pass


def _invalidate_user_cache(user_id, org_id):
    cache.delete(f"notifications:unread_count:{user_id}:{org_id}")
    cache.delete(f"dashboard:notifications:{user_id}:{org_id}:summary")
    _safe_delete_pattern(f"dashboard:notifications:{user_id}:{org_id}:recent*")


def _get_priority(type_):
    return PRIORITY_MAP.get(type_, "info")


def _resolve_organization(product=None, location=None):
    if product and hasattr(product, "organization_id"):
        return product.organization
    if location and hasattr(location, "organization_id"):
        return location.organization
    return None


def _get_target_users(organization):
    from notifications.preferences import ensure_user_preferences

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

    message = _build_message(type_, product, location)

    notification = Notification.objects.create(
        organization=organization,
        product=product,
        location=location,
        type=type_,
        priority=_get_priority(type_),
        message=message,
        is_active=True,
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