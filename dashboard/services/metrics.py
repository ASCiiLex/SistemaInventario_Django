from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, F, Value, Count
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

    # 🔥 optimización: evitar joins innecesarios a nivel Python
    qs = (
        StockItem.objects
        .select_related("product")
        .filter(quantity__lte=F("min_stock"))
        .values(
            "product__id",
            "product__name"
        )
        .annotate(
            quantity=Coalesce(Sum("quantity"), Value(0)),
            min_stock=Coalesce(Sum("min_stock"), Value(0)),
        )
    )

    result = [
        {
            "product": {
                "id": row["product__id"],
                "name": row["product__name"],
            },
            "quantity": row["quantity"],
            "min_stock": row["min_stock"],
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

    # 🔥 optimización: evitar DISTINCT costoso
    low_stock_count = (
        StockItem.objects
        .filter(quantity__lte=F("min_stock"))
        .values("product")
        .annotate(c=Count("id"))
        .count()
    )

    result = {
        "total_products": Product.objects.only("id").count(),
        "total_suppliers": Supplier.objects.only("id").count(),
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
    }

    cache.set(cache_key, result, settings.CACHE_TTL["metrics"])
    return result