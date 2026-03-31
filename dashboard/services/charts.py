from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockItem, StockMovement


def invalidate_chart_cache():
    keys = [
        "dashboard:chart:category",
        "dashboard:chart:supplier",
        "dashboard:chart:location",
        "dashboard:chart:rotation",
        "dashboard:chart:movements",
    ]
    for k in keys:
        cache.delete(k)


def _format_result(qs, label_field, value_field):
    labels = []
    values = []

    for row in qs:
        labels.append(row[label_field] or "Sin dato")
        values.append(row[value_field] or 0)

    return labels, values


def get_chart_by_category():
    cache_key = "dashboard:chart:category"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        Category.objects
        .values("name")
        .annotate(total=Coalesce(Sum("products__stock_items__quantity"), Value(0)))
        .order_by("name")
    )

    result = _format_result(qs, "name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_by_supplier():
    cache_key = "dashboard:chart:supplier"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        Supplier.objects
        .values("name")
        .annotate(total=Coalesce(Sum("products__stock_items__quantity"), Value(0)))
        .order_by("name")
    )

    result = _format_result(qs, "name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_by_location():
    cache_key = "dashboard:chart:location"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockItem.objects
        .values("location__name")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("location__name")
    )

    result = _format_result(qs, "location__name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_rotation_by_product():
    cache_key = "dashboard:chart:rotation"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockMovement.objects
        .values("product__name")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("-total")[:10]
    )

    result = _format_result(qs, "product__name", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result


def get_chart_movements_by_type():
    cache_key = "dashboard:chart:movements"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockMovement.objects
        .values("movement_type")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("movement_type")
    )

    result = _format_result(qs, "movement_type", "total")
    cache.set(cache_key, result, settings.CACHE_TTL["charts"])
    return result