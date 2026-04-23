from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

import logging

from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockItem, StockMovement

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


def invalidate_chart_cache(org_id=None):
    try:
        if org_id:
            keys = [
                f"dashboard:chart:category:{org_id}",
                f"dashboard:chart:supplier:{org_id}",
                f"dashboard:chart:location:{org_id}",
                f"dashboard:chart:rotation:{org_id}",
                f"dashboard:chart:movements:{org_id}",
            ]
            for k in keys:
                cache.delete(k)
        else:
            cache.clear()
    except Exception:
        pass


def _format_result(qs, label_field, value_field):
    labels = []
    values = []

    for row in qs:
        labels.append(row[label_field] or "Sin dato")
        values.append(row[value_field] or 0)

    return labels, values


def _cache_get_or_set(key, org_id, fn):
    cached = _safe_cache_get(key)
    if cached:
        metrics_logger.info("dashboard.cache.hit.chart", extra={"org_id": org_id, "key": key})
        return cached

    result = fn()

    ttl = getattr(settings, "CACHE_TTL", {}).get("charts", 60)
    _safe_cache_set(key, result, ttl)

    metrics_logger.info("dashboard.cache.miss.chart", extra={"org_id": org_id, "key": key})

    return result


def get_chart_by_category(organization):
    key = f"dashboard:chart:category:{organization.id}"

    def compute():
        qs = (
            Category.objects
            .filter(organization=organization)
            .values("name")
            .annotate(total=Coalesce(Sum("products__stock_items__quantity"), Value(0)))
        )
        return _format_result(qs, "name", "total")

    return _cache_get_or_set(key, organization.id, compute)


def get_chart_by_supplier(organization):
    key = f"dashboard:chart:supplier:{organization.id}"

    def compute():
        qs = (
            Supplier.objects
            .filter(organization=organization)
            .values("name")
            .annotate(total=Coalesce(Sum("products__stock_items__quantity"), Value(0)))
        )
        return _format_result(qs, "name", "total")

    return _cache_get_or_set(key, organization.id, compute)


def get_chart_by_location(organization):
    key = f"dashboard:chart:location:{organization.id}"

    def compute():
        qs = (
            StockItem.objects
            .filter(organization=organization)
            .values("location__name")
            .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        )
        return _format_result(qs, "location__name", "total")

    return _cache_get_or_set(key, organization.id, compute)


def get_chart_rotation_by_product(organization):
    key = f"dashboard:chart:rotation:{organization.id}"

    def compute():
        qs = (
            StockMovement.objects
            .filter(organization=organization)
            .values("product__name")
            .annotate(total=Coalesce(Sum("quantity"), Value(0)))
            .order_by("-total")[:10]
        )
        return _format_result(qs, "product__name", "total")

    return _cache_get_or_set(key, organization.id, compute)


def get_chart_movements_by_type(organization):
    key = f"dashboard:chart:movements:{organization.id}"

    def compute():
        qs = (
            StockMovement.objects
            .filter(organization=organization)
            .values("movement_type")
            .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        )
        return _format_result(qs, "movement_type", "total")

    return _cache_get_or_set(key, organization.id, compute)