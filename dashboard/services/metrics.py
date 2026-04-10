from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Value, F, DecimalField, ExpressionWrapper, IntegerField
from django.db.models.functions import Coalesce

import logging
import time

from products.models import Product
from inventory.models import StockItem, Order, StockMovement

metrics_logger = logging.getLogger("inventory.metrics")


def invalidate_metrics_cache(org_id=None):
    if org_id:
        cache.delete(f"dashboard:metrics:{org_id}")
        cache.delete(f"dashboard:low_stock:{org_id}")
        cache.delete(f"dashboard:system_metrics:{org_id}")
    else:
        cache.clear()


# ==========================================
# EXISTENTES (SIN CAMBIO FUNCIONAL)
# ==========================================

def get_low_stock(organization):
    cache_key = f"dashboard:low_stock:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        metrics_logger.info("dashboard.cache.hit.low_stock", extra={"org_id": organization.id})
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

    metrics_logger.info("dashboard.cache.miss.low_stock", extra={
        "org_id": organization.id,
        "count": len(result)
    })

    return result


def get_products_at_risk(organization):
    return Product.objects.filter(
        organization=organization
    ).annotate(
        total_stock=Coalesce(Sum("stock_items__quantity"), Value(0, output_field=IntegerField())),
        total_min=Coalesce(Sum("stock_items__min_stock"), Value(0, output_field=IntegerField())),
    ).filter(total_stock__lte=F("total_min"))


def get_dashboard_metrics(organization):
    cache_key = f"dashboard:metrics:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        metrics_logger.info("dashboard.cache.hit.metrics", extra={"org_id": organization.id})
        return cached

    total_units = (
        StockItem.objects
        .filter(organization=organization)
        .aggregate(
            total=Coalesce(
                Sum("quantity"),
                Value(0, output_field=IntegerField())
            )
        )
    )["total"]

    inventory_value = (
        StockItem.objects
        .select_related("product")
        .filter(organization=organization)
        .annotate(
            total_value=ExpressionWrapper(
                F("quantity") * F("product__cost_price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        .aggregate(
            total=Coalesce(
                Sum("total_value"),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
            )
        )
    )["total"]

    pending_orders = Order.objects.filter(
        organization=organization,
        status__in=["pending", "partially_received", "backordered"]
    ).count()

    product_risk_count = get_products_at_risk(organization).count()

    result = {
        "total_units": total_units,
        "inventory_value": inventory_value,
        "pending_orders": pending_orders,
        "product_risk_count": product_risk_count,
    }

    cache.set(cache_key, result, settings.CACHE_TTL["metrics"])

    metrics_logger.info("dashboard.metrics.calculated", extra={
        "org_id": organization.id,
        "total_units": total_units,
        "inventory_value": float(inventory_value),
        "pending_orders": pending_orders,
        "product_risk_count": product_risk_count,
    })

    return result


# ==========================================
# 🔥 NUEVO — MÉTRICAS INTERNAS
# ==========================================

def get_system_metrics(organization):
    cache_key = f"dashboard:system_metrics:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        metrics_logger.info("dashboard.cache.hit.system_metrics", extra={"org_id": organization.id})
        return cached

    start = time.time()

    movements_last_24h = StockMovement.objects.filter(
        organization=organization
    ).count()

    errors_estimate = 0  # 🔥 placeholder para futuro (logs parsing / prometheus)

    cache_size = cache._cache.get_client().dbsize() if hasattr(cache, "_cache") else 0

    duration = time.time() - start

    result = {
        "movements_24h": movements_last_24h,
        "errors": errors_estimate,
        "cache_keys": cache_size,
        "calc_time": round(duration, 4),
    }

    cache.set(cache_key, result, 10)

    metrics_logger.info("dashboard.system_metrics.calculated", extra={
        "org_id": organization.id,
        **result
    })

    return result