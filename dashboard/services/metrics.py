from django.db.models import Sum, F, Count, Q, Value
from django.db.models.functions import Coalesce

from products.models import Product
from suppliers.models import Supplier
from inventory.models import StockItem


def get_low_stock():
    products = (
        Product.objects
        .annotate(
            total_stock_db=Coalesce(Sum("stock_items__quantity"), Value(0)),
            total_min_stock_db=Coalesce(Sum("stock_items__min_stock"), Value(0)),
        )
        .filter(total_stock_db__lte=F("total_min_stock_db"))
        .only("id", "name")
    )

    return [
        {
            "product": p,
            "quantity": p.total_stock_db,
            "min_stock": p.total_min_stock_db,
        }
        for p in products
    ]


def get_dashboard_metrics():
    aggregated = StockItem.objects.aggregate(
        total_stock=Coalesce(Sum("quantity"), Value(0)),
    )

    low_stock_products = (
        StockItem.objects
        .filter(quantity__lte=F("min_stock"))
        .values("product")
        .distinct()
        .count()
    )

    return {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": aggregated["total_stock"],
        "low_stock_count": low_stock_products,
    }