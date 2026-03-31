from django.core.cache import cache

from inventory.models import StockItem
from products.models import Product
from notifications.events import emit_event


def invalidate_dashboard_cache():
    keys = [
        "dashboard:metrics",
        "dashboard:low_stock",
        "dashboard:chart:category",
        "dashboard:chart:supplier",
        "dashboard:chart:location",
        "dashboard:chart:rotation",
        "dashboard:chart:movements",
        "dashboard:notifications:summary",
    ]
    cache.delete_many(keys)


def sync_stock_item_notifications():
    items = StockItem.objects.select_related("product", "location")

    for item in items:
        if item.quantity <= item.min_stock:

            emit_event(
                "stock_item_low",
                {
                    "product": item.product,
                    "location": item.location,
                    "message": f"{item.product.name} bajo mínimo en {item.location.name}",
                }
            )


def sync_product_risk_notifications():
    products = Product.objects.all()

    for p in products:
        if p.total_stock <= p.total_min_stock:

            emit_event(
                "product_risk",
                {
                    "product": p,
                    "message": f"Producto en riesgo: {p.name}",
                }
            )


def sync_all_notifications():
    sync_stock_item_notifications()
    sync_product_risk_notifications()

    invalidate_dashboard_cache()