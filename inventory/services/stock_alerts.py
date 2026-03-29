from inventory.models import StockItem
from products.models import Product

from notifications.services import create_notification


def sync_stock_item_notifications():
    items = StockItem.objects.select_related("product", "location")

    for item in items:
        if item.quantity <= item.min_stock:

            create_notification(
                product=item.product,
                location=item.location,
                type_="stock_item_low",
                message=f"{item.product.name} bajo mínimo en {item.location.name}",
            )


def sync_product_risk_notifications():
    products = Product.objects.all()

    for p in products:
        if p.total_stock <= p.total_min_stock:

            create_notification(
                product=p,
                type_="product_risk",
                message=f"Producto en riesgo: {p.name}",
            )


def sync_all_notifications():
    sync_stock_item_notifications()
    sync_product_risk_notifications()