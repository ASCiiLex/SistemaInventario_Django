from django.core.cache import cache
from django.conf import settings
from inventory.models import StockMovement


def invalidate_activity_cache():
    cache.delete("dashboard:activity:recent")
    cache.delete("dashboard:activity:all")


def get_recent_movements(limit=10):
    cache_key = f"dashboard:activity:recent:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = list(
        StockMovement.objects
        .select_related("product", "origin", "destination")
        .only(
            "id",
            "quantity",
            "movement_type",
            "created_at",
            "product__name",
            "origin__name",
            "destination__name",
        )
        .exclude(origin__isnull=True, destination__isnull=True)
        .order_by("-created_at")[:limit]
    )

    cache.set(cache_key, qs, settings.CACHE_TTL["activity"])
    return qs


def get_all_stock_movements():
    cache_key = "dashboard:activity:all"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = list(
        StockMovement.objects
        .select_related("product")
        .only(
            "id",
            "quantity",
            "movement_type",
            "created_at",
            "product__name",
        )
        .order_by("-created_at")
    )

    cache.set(cache_key, qs, settings.CACHE_TTL["activity"])
    return qs