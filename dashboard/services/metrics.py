from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Value, Count, F
from django.db.models.functions import Coalesce

from products.models import Product
from suppliers.models import Supplier
from inventory.models import StockItem


def invalidate_metrics_cache():
    cache.delete("dashboard:metrics")
    cache.delete("dashboard:low_stock")


def get_low_stock():
    cache_key = "dashboard:low_stock"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        Product.objects
        .annotate(
            total_stock=Coalesce(Sum("stock_items__quantity"), Value(0)),
            total_min_stock=Coalesce(Sum("stock_items__min_stock"), Value(0)),
        )
        .filter(total_stock__lte=F("total_min_stock"))
        .values("id", "name", "total_stock", "total_min_stock")
    )

    result = [
        {
            "product": {
                "id": row["id"],
                "name": row["name"],
            },
            "quantity": row["total_stock"],
            "min_stock": row["total_min_stock"],
        }
        for row in qs
    ]

    cache.set(cache_key, result, settings.CACHE_TTL["low_stock"])
    return result


def get_dashboard_metrics():
    cache_key = "dashboard:metrics"
    cached = cache.get(cache_key)
    if cached:
        return cached

    total_stock = (
        StockItem.objects.aggregate(
            total=Coalesce(Sum("quantity"), Value(0))
        )["total"]
    )

    low_stock_count = (
        Product.objects
        .annotate(
            total_stock=Coalesce(Sum("stock_items__quantity"), Value(0)),
            total_min_stock=Coalesce(Sum("stock_items__min_stock"), Value(0)),
        )
        .filter(total_stock__lte=F("total_min_stock"))
        .count()
    )

    result = {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
    }

    cache.set(cache_key, result, settings.CACHE_TTL["metrics"])
    return result