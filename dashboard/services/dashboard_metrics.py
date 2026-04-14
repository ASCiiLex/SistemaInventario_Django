from django.db import models

from products.models import Product
from inventory.models import StockItem


def get_dashboard_metrics(org):
    return {
        "total_products": Product.objects.filter(organization=org).count(),
        "total_stock": StockItem.objects.filter(organization=org).count(),
    }


def get_low_stock(org):
    return StockItem.objects.filter(
        organization=org,
        quantity__lte=models.F("min_stock")
    ).select_related("product")