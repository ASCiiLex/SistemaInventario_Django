from django.core.cache import cache
from django.conf import settings
from inventory.models import StockMovement


def invalidate_activity_cache(org_id=None):
    if org_id:
        cache.delete(f"dashboard:activity:recent:{org_id}")
        cache.delete(f"dashboard:activity:all:{org_id}")
    else:
        cache.clear()


def get_recent_movements(organization, limit=10):
    cache_key = f"dashboard:activity:recent:{organization.id}:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = list(
        StockMovement.objects
        .filter(organization=organization)
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
        .order_by("-created_at")[:limit]
    )

    cache.set(cache_key, qs, settings.CACHE_TTL["activity"])
    return qs


def get_all_stock_movements(organization):
    cache_key = f"dashboard:activity:all:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = list(
        StockMovement.objects
        .filter(organization=organization)
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