from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q

from notifications.models import Notification


def invalidate_notifications_cache():
    cache.delete("dashboard:notifications:summary")
    cache.delete("dashboard:notifications:recent")
    cache.delete("notifications:unread_count")


def get_notifications_summary():
    cache_key = "dashboard:notifications:summary"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = Notification.objects.all()

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

    by_type_raw = qs.values("type").annotate(total=Count("id"))

    by_type = [
        {
            "type": item["type"],
            "label": TYPE_LABELS.get(item["type"], item["type"]),
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


def get_recent_notifications(limit=10):
    cache_key = f"dashboard:notifications:recent:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = list(
        Notification.objects
        .select_related("product", "location")
        .only(
            "id",
            "message",
            "type",
            "priority",
            "seen",
            "created_at",
            "product__name",
            "location__name",
        )
        .order_by("-created_at")[:limit]
    )

    cache.set(cache_key, qs, settings.CACHE_TTL["notifications"])
    return qs