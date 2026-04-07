from django.core.cache import cache

from inventory.models import StockItem
from products.models import Product
from notifications.events import emit_event
from notifications.constants import Events


def invalidate_dashboard_cache(org_id=None):
    if not org_id:
        return

    keys = [
        f"dashboard:metrics:{org_id}",
        f"dashboard:low_stock:{org_id}",
        f"dashboard:chart:category:{org_id}",
        f"dashboard:chart:supplier:{org_id}",
        f"dashboard:chart:location:{org_id}",
        f"dashboard:chart:rotation:{org_id}",
        f"dashboard:chart:movements:{org_id}",
        f"dashboard:notifications:summary:{org_id}",
    ]
    cache.delete_many(keys)


def sync_stock_item_notifications(organization):
    items = (
        StockItem.objects
        .select_related("product", "location")
        .filter(organization=organization)
    )

    for item in items:
        if item.quantity <= item.min_stock:
            emit_event(
                Events.STOCK_LOW,
                {
                    "product": item.product,
                    "location": item.location,
                    "message": f"Stock bajo en {item.location.name}: {item.product.name}",
                }
            )


def sync_product_risk_notifications(organization):
    products = Product.objects.filter(organization=organization)

    for p in products:
        if p.total_stock <= p.total_min_stock:
            emit_event(
                Events.PRODUCT_RISK,
                {
                    "product": p,
                    "message": f"Producto en riesgo: {p.name}",
                }
            )


def sync_all_notifications(organization):
    sync_stock_item_notifications(organization)
    sync_product_risk_notifications(organization)

    invalidate_dashboard_cache(organization.id)