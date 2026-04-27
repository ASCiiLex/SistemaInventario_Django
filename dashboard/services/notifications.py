from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q
from collections import defaultdict

import logging

from notifications.models import UserNotification
from notifications.constants import Events

metrics_logger = logging.getLogger("inventory.metrics")


def _safe_cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def _safe_cache_set(key, value, ttl):
    try:
        cache.set(key, value, ttl)
    except Exception:
        pass


def _cache_key(user_id, org_id, suffix):
    return f"dashboard:notifications:{user_id}:{org_id}:{suffix}"


def invalidate_notifications_cache(user_id=None, org_id=None):
    try:
        if user_id and org_id:
            cache.delete(_cache_key(user_id, org_id, "summary"))
            cache.delete(_cache_key(user_id, org_id, "recent"))
        else:
            cache.clear()
    except Exception:
        pass


TYPE_LABELS = {
    Events.STOCK_LOW: "Stock bajo",
    Events.PRODUCT_RISK: "Producto en riesgo",
    Events.MOVEMENT_CREATED: "Movimiento",
    Events.ORDERS_UPDATED: "Pedido",
}


def get_notifications_summary(user, organization):
    cache_key = _cache_key(user.id, organization.id, "summary")
    cached = _safe_cache_get(cache_key)

    if cached:
        metrics_logger.info(
            "dashboard.cache.hit.notifications_summary",
            extra={"org_id": organization.id, "user_id": user.id}
        )
        return cached

    qs = (
        UserNotification.objects
        .filter(
            user=user,
            notification__organization=organization
        )
        .select_related("notification")
    )

    aggregated = qs.aggregate(
        total=Count("id"),
        unread=Count("id", filter=Q(seen=False)),
    )

    by_type_raw = (
        qs.values("notification__type")
        .annotate(total=Count("id"))
    )

    by_type = [
        {
            "type": item["notification__type"],
            "label": TYPE_LABELS.get(
                item["notification__type"],
                item["notification__type"]
            ),
            "total": item["total"],
        }
        for item in by_type_raw
    ]

    result = {
        "notifications_total": aggregated["total"],
        "notifications_unread": aggregated["unread"],
        "notifications_by_type": by_type,
    }

    ttl = getattr(settings, "CACHE_TTL", {}).get("notifications", 60)
    _safe_cache_set(cache_key, result, ttl)

    metrics_logger.info(
        "dashboard.cache.miss.notifications_summary",
        extra={
            "org_id": organization.id,
            "user_id": user.id,
            "total": aggregated["total"],
            "unread": aggregated["unread"],
            "types_count": len(by_type),
        }
    )

    return result


def get_recent_notifications(user, organization, limit=10):
    cache_key = _cache_key(user.id, organization.id, "recent")
    cached = _safe_cache_get(cache_key)

    if cached:
        metrics_logger.info(
            "dashboard.cache.hit.notifications_recent",
            extra={"org_id": organization.id, "user_id": user.id}
        )
        return cached

    qs = (
        UserNotification.objects
        .filter(
            user=user,
            notification__organization=organization
        )
        .select_related("notification__product", "notification__location")
        .order_by("-notification__created_at")[:limit]
    )

    result = list(qs)

    ttl = getattr(settings, "CACHE_TTL", {}).get("notifications", 60)
    _safe_cache_set(cache_key, result, ttl)

    metrics_logger.info(
        "dashboard.cache.miss.notifications_recent",
        extra={
            "org_id": organization.id,
            "user_id": user.id,
            "count": len(result),
        }
    )

    return result


def _get_icon(notification_type):
    if notification_type == Events.PRODUCT_RISK:
        return "⚠️"
    elif notification_type == Events.STOCK_LOW:
        return "🔴"
    return "🔔"


def get_grouped_notifications(user, organization, limit_per_group=1, history_limit=20):
    qs = (
        UserNotification.objects
        .filter(
            user=user,
            notification__organization=organization
        )
        .select_related("notification__product", "notification__location")
        .order_by("-notification__created_at")
    )

    grouped = defaultdict(list)

    for un in qs:
        key = (
            un.notification.product_id,
            un.notification.type
        )
        grouped[key].append(un)

    result = []

    for (_, _), items in grouped.items():
        visible = items[:limit_per_group]
        hidden = items[limit_per_group:limit_per_group + history_limit]

        icons = set()

        visible_items = []
        hidden_items = []

        for un in items:
            icon = _get_icon(un.notification.type)
            icons.add(icon)

        for un in visible:
            visible_items.append({
                "obj": un,
                "icon": _get_icon(un.notification.type),
            })

        for un in hidden:
            hidden_items.append({
                "obj": un,
                "icon": _get_icon(un.notification.type),
            })

        result.append({
            "product": items[0].notification.product,
            "count": len(items),
            "items": visible_items,
            "hidden_items": hidden_items,
            "hidden_count": max(0, len(items) - len(visible)),
            "icons": list(icons),
        })

    return result