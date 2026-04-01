from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q

from notifications.models import UserNotification


def _cache_key(user_id, suffix):
    return f"dashboard:notifications:{user_id}:{suffix}"


def invalidate_notifications_cache(user_id=None):
    if user_id:
        cache.delete(_cache_key(user_id, "summary"))
        cache.delete(_cache_key(user_id, "recent"))
    else:
        # fallback global (por si acaso)
        cache.clear()


def get_notifications_summary(user):
    cache_key = _cache_key(user.id, "summary")
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = UserNotification.objects.filter(user=user).select_related("notification")

    aggregated = qs.aggregate(
        total=Count("id"),
        unread=Count("id", filter=Q(seen=False)),
    )

    TYPE_LABELS = {
        "stock_item_low": "Incidencia almacén",
        "product_risk": "Producto en riesgo",
        "order": "Pedido",
        "movement": "Movimiento",
    }

    by_type_raw = (
        qs.values("notification__type")
        .annotate(total=Count("id"))
    )

    by_type = [
        {
            "type": item["notification__type"],
            "label": TYPE_LABELS.get(item["notification__type"], item["notification__type"]),
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
    return result


def get_recent_notifications(user, limit=10):
    cache_key = _cache_key(user.id, f"recent:{limit}")
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = list(
        UserNotification.objects
        .filter(user=user)
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
    return qs