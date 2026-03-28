from django.db.models import Sum, F

from products.models import Product
from suppliers.models import Supplier
from inventory.models import StockItem


def get_low_stock():
    products = Product.objects.annotate(
        total_stock_db=Sum("stock_items__quantity"),
        total_min_stock_db=Sum("stock_items__min_stock"),
    ).filter(
        total_stock_db__lte=F("total_min_stock_db")
    )

    low_stock = []

    for p in products:
        low_stock.append({
            "product": p,
            "quantity": p.total_stock_db or 0,
            "min_stock": p.total_min_stock_db or 0,
        })

    return low_stock


def get_dashboard_metrics():
    total_stock = StockItem.objects.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    low_stock_list = get_low_stock()

    return {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": total_stock,
        "low_stock_count": len(low_stock_list),
    }