from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockItem, StockMovement


def invalidate_chart_cache(org_id=None):
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


def _format_result(qs, label_field, value_field):
    labels = []
    values = []

    for row in qs:
        labels.append(row[label_field] or "Sin dato")
        values.append(row[value_field] or 0)

    return labels, values


def get_chart_by_category(organization):
    cache_key = f"dashboard:chart:category:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        Category.objects
        .filter(organization=organization)
        .values("name")
        .annotate(total=Coalesce(Sum("products__stock_items__quantity"), Value(0)))
        .order_by("name")
    )

    result = _format_result(qs, "name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_by_supplier(organization):
    cache_key = f"dashboard:chart:supplier:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        Supplier.objects
        .filter(organization=organization)
        .values("name")
        .annotate(total=Coalesce(Sum("products__stock_items__quantity"), Value(0)))
        .order_by("name")
    )

    result = _format_result(qs, "name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_by_location(organization):
    cache_key = f"dashboard:chart:location:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockItem.objects
        .filter(organization=organization)
        .values("location__name")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("location__name")
    )

    result = _format_result(qs, "location__name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_rotation_by_product(organization):
    cache_key = f"dashboard:chart:rotation:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockMovement.objects
        .filter(organization=organization)
        .values("product__name")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("-total")[:10]
    )

    result = _format_result(qs, "product__name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_movements_by_type(organization):
    cache_key = f"dashboard:chart:movements:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockMovement.objects
        .filter(organization=organization)
        .values("movement_type")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("movement_type")
    )

    result = _format_result(qs, "movement_type", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result