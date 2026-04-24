from django.core.cache import cache
from django.db.models import Sum, F

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


# 🔥 SOLO PARA USO MANUAL / BATCH (NO EN REQUEST)
def sync_all_notifications(organization):
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
                }
            )

    products = Product.objects.filter(organization=organization)

    for p in products:

        agg = (
            StockItem.objects
            .filter(organization=organization, product=p)
            .aggregate(
                total_qty=Sum("quantity"),
                total_min=Sum("min_stock"),
            )
        )

        total_qty = agg["total_qty"] or 0
        total_min = agg["total_min"] or 0

        has_local_issue = StockItem.objects.filter(
            organization=organization,
            product=p,
            quantity__lte=F("min_stock")
        ).exists()

        if has_local_issue and total_qty <= total_min:
            emit_event(
                Events.PRODUCT_RISK,
                {
                    "product": p,
                }
            )

    invalidate_dashboard_cache(organization.id)