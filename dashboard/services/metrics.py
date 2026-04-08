from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Value, F
from django.db.models.functions import Coalesce

from products.models import Product
from suppliers.models import Supplier
from inventory.models import StockItem


def invalidate_metrics_cache(org_id=None):
    if org_id:
        cache.delete(f"dashboard:metrics:{org_id}")
        cache.delete(f"dashboard:low_stock:{org_id}")
    else:
        cache.clear()


def get_low_stock(organization):
    cache_key = f"dashboard:low_stock:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = (
        StockItem.objects
        .select_related("product", "location")
        .filter(
            organization=organization,
            quantity__lte=F("min_stock")
        )
    )

    result = [
        {
            "product": {
                "id": item.product.id,
                "name": item.product.name,
            },
            "location": {
                "id": item.location.id,
                "name": item.location.name,
            },
            "quantity": item.quantity,
            "min_stock": item.min_stock,
        }
        for item in qs
    ]

    cache.set(cache_key, result, settings.CACHE_TTL["low_stock"])
    return result


def get_products_at_risk(organization):
    return Product.objects.filter(
        organization=organization
    ).annotate(
        total_stock=Coalesce(Sum("stock_items__quantity"), Value(0)),
        total_min=Coalesce(Sum("stock_items__min_stock"), Value(0)),
    ).filter(total_stock__lte=F("total_min"))


def get_dashboard_metrics(organization):
    cache_key = f"dashboard:metrics:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    total_stock = (
        StockItem.objects
        .filter(organization=organization)
        .aggregate(total=Coalesce(Sum("quantity"), Value(0)))
    )["total"]

    low_stock = get_low_stock(organization)
    products_at_risk = get_products_at_risk(organization)

    result = {
        "total_products": Product.objects.filter(organization=organization).count(),
        "total_suppliers": Supplier.objects.filter(organization=organization).count(),
        "total_stock": total_stock,
        "low_stock_count": len(low_stock),
        "product_risk_count": products_at_risk.count(),
    }

    cache.set(cache_key, result, settings.CACHE_TTL["metrics"])
    return result