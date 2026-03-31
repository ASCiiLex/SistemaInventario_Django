from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockItem, StockMovement


def _format_result(qs, label_field, value_field):
    labels = []
    values = []

    for row in qs:
        labels.append(row[label_field] or "Sin dato")
        values.append(row[value_field] or 0)

    return labels, values


def get_chart_by_category():
    qs = (
        Category.objects
        .values("name")
        .annotate(
            total=Coalesce(Sum("products__stock_items__quantity"), Value(0))
        )
        .order_by("name")
    )

    return _format_result(qs, "name", "total")


def get_chart_by_supplier():
    qs = (
        Supplier.objects
        .values("name")
        .annotate(
            total=Coalesce(Sum("products__stock_items__quantity"), Value(0))
        )
        .order_by("name")
    )

    return _format_result(qs, "name", "total")


def get_chart_by_location():
    qs = (
        StockItem.objects
        .values("location__name")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("location__name")
    )

    return _format_result(qs, "location__name", "total")


def get_chart_rotation_by_product():
    qs = (
        StockMovement.objects
        .values("product__name")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("-total")[:10]
    )

    return _format_result(qs, "product__name", "total")


def get_chart_movements_by_type():
    qs = (
        StockMovement.objects
        .values("movement_type")
        .annotate(total=Coalesce(Sum("quantity"), Value(0)))
        .order_by("movement_type")
    )

    return _format_result(qs, "movement_type", "total")