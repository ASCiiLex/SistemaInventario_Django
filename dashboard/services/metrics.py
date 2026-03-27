from django.db.models import Sum

from products.models import Product
from suppliers.models import Supplier
from inventory.models import StockItem


def _get_real_stock_for_product(product):
    qty = product.stock_items.aggregate(total=Sum("quantity"))["total"]
    if qty is None:
        return product.stock or 0
    return qty


def get_low_stock():
    low_stock = []
    products = Product.objects.all().prefetch_related("stock_items")

    for p in products:
        current_stock = _get_real_stock_for_product(p)
        if current_stock <= (p.min_stock or 0):
            low_stock.append(
                {
                    "product": p,
                    "quantity": current_stock,
                    "min_stock": p.min_stock,
                }
            )

    return low_stock


def get_dashboard_metrics():
    total_stock_real = StockItem.objects.aggregate(total=Sum("quantity"))["total"]
    if total_stock_real is None:
        total_stock_real = Product.objects.aggregate(total=Sum("stock"))["total"] or 0

    low_stock_list = get_low_stock()

    return {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": total_stock_real,
        "low_stock_count": len(low_stock_list),
    }