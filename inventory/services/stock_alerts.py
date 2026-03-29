from django.apps import apps
from inventory.models import StockItem


def sync_stock_item_notifications():
    Notification = apps.get_model("notifications", "Notification")

    items = StockItem.objects.select_related("product", "location")

    for item in items:
        if item.quantity <= item.min_stock:

            if Notification.recently_created(
                product=item.product,
                location=item.location,
                type="stock_item_low",
                minutes=30
            ):
                continue

            Notification.objects.create(
                product=item.product,
                location=item.location,
                type="stock_item_low",
                priority="critical",
                message=f"{item.product.name} bajo mínimo en {item.location.name}",
            )


def sync_product_risk_notifications():
    Notification = apps.get_model("notifications", "Notification")
    from products.models import Product

    products = Product.objects.all()

    for p in products:
        if p.total_stock <= p.total_min_stock:

            if Notification.recently_created(
                product=p,
                type="product_risk",
                minutes=60
            ):
                continue

            Notification.objects.create(
                product=p,
                type="product_risk",
                priority="warning",
                message=f"Producto en riesgo: {p.name}",
            )


def sync_all_notifications():
    sync_stock_item_notifications()
    sync_product_risk_notifications()