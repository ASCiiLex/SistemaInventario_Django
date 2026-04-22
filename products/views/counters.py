from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce

from products.models import Product
from inventory.models import StockItem


def lowstock_counter(request):
    count = (
        Product.objects
        .filter(organization=request.organization)
        .annotate(
            total_stock=Coalesce(Sum("stock_items__quantity"), Value(0)),
            total_min_stock=Coalesce(Sum("stock_items__min_stock"), Value(0)),
        )
        .filter(total_stock__lte=F("total_min_stock"))
        .count()
    )

    html = render_to_string(
        "products/partials/lowstock_counter.html",
        {"count": count}
    )

    response = HttpResponse(html)
    response["HX-Trigger"] = '{"inventory:stock_changed": true}'
    return response


def stockitem_counter(request):
    count = StockItem.objects.filter(
        organization=request.organization,
        quantity__lte=F("min_stock")
    ).count()

    html = render_to_string(
        "products/partials/stockitem_counter.html",
        {"count": count}
    )

    response = HttpResponse(html)
    response["HX-Trigger"] = '{"inventory:stock_changed": true}'
    return response