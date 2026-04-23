from django.core.cache import cache
from django.conf import settings

import logging

from inventory.models import StockMovement

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


def invalidate_activity_cache(org_id=None):
    try:
        if org_id:
            cache.delete(f"dashboard:activity:recent:{org_id}")
            cache.delete(f"dashboard:activity:all:{org_id}")
        else:
            cache.clear()
    except Exception:
        pass


def get_recent_movements(organization, limit=10):
    cache_key = f"dashboard:activity:recent:{organization.id}:{limit}"
    cached = _safe_cache_get(cache_key)
    if cached:
        metrics_logger.info("dashboard.cache.hit.activity_recent", extra={"org_id": organization.id})
        return cached

    qs = list(
        StockMovement.objects
        .filter(organization=organization)
        .select_related("product", "origin", "destination")
        .order_by("-created_at")[:limit]
    )

    ttl = getattr(settings, "CACHE_TTL", {}).get("activity", 60)
    _safe_cache_set(cache_key, qs, ttl)

    metrics_logger.info("dashboard.cache.miss.activity_recent", extra={
        "org_id": organization.id,
        "count": len(qs)
    })

    return qs


def get_all_stock_movements(organization):
    cache_key = f"dashboard:activity:all:{organization.id}"
    cached = _safe_cache_get(cache_key)
    if cached:
        metrics_logger.info("dashboard.cache.hit.activity_all", extra={"org_id": organization.id})
        return cached

    qs = list(
        StockMovement.objects
        .filter(organization=organization)
        .select_related("product")
        .order_by("-created_at")
    )

    ttl = getattr(settings, "CACHE_TTL", {}).get("activity", 60)
    _safe_cache_set(cache_key, qs, ttl)

    metrics_logger.info("dashboard.cache.miss.activity_all", extra={
        "org_id": organization.id,
        "count": len(qs)
    })

    return qs