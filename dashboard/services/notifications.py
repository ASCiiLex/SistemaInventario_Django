from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q

import logging

from notifications.models import UserNotification
from notifications.constants import Events

metrics_logger = logging.getLogger("inventory.metrics")


# ==========================================
# CACHE KEYS
# ==========================================

def _cache_key(user_id, org_id, suffix):
    return f"dashboard:notifications:{user_id}:{org_id}:{suffix}"


def invalidate_notifications_cache(user_id=None, org_id=None):
    if user_id and org_id:
        cache.delete(_cache_key(user_id, org_id, "summary"))
        cache.delete(_cache_key(user_id, org_id, "recent"))
    else:
        cache.clear()


# ==========================================
# LABELS
# ==========================================

TYPE_LABELS = {
    Events.STOCK_LOW: "Stock bajo",
    Events.PRODUCT_RISK: "Producto en riesgo",
    Events.MOVEMENT_CREATED: "Movimiento",
    Events.ORDERS_UPDATED: "Pedido",
}


# ==========================================
# SUMMARY
# ==========================================

def get_notifications_summary(user, organization):
    cache_key = _cache_key(user.id, organization.id, "summary")
    cached = cache.get(cache_key)

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

    cache.set(cache_key, result, settings.CACHE_TTL["notifications"])

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


# ==========================================
# RECENT
# ==========================================

def get_recent_notifications(user, organization, limit=10):
    cache_key = _cache_key(user.id, organization.id, f"recent:{limit}")
    cached = cache.get(cache_key)

    if cached:
        metrics_logger.info(
            "dashboard.cache.hit.notifications_recent",
            extra={"org_id": organization.id, "user_id": user.id}
        )
        return cached

    qs = list(
        UserNotification.objects
        .filter(
            user=user,
            notification__organization=organization
        )
        .select_related("notification__product", "notification__location")
        .only(
            "id",
            "seen",
            "notification__id",
            "notification__message",
            "notification__type",
            "notification__priority",
            "notification__created_at",
            "notification__product__name",
            "notification__location__name",
        )
        .order_by("-notification__created_at")[:limit]
    )

    cache.set(cache_key, qs, settings.CACHE_TTL["notifications"])

    metrics_logger.info(
        "dashboard.cache.miss.notifications_recent",
        extra={
            "org_id": organization.id,
            "user_id": user.id,
            "count": len(qs),
            "limit": limit,
        }
    )

    return qs