from django.db.models import Sum

from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockItem, StockMovement


def get_chart_by_category():
    categories = (
        Category.objects
        .annotate(
            total_stock_items=Sum("products__stock_items__quantity"),
            total_product_stock=Sum("products__stock"),
        )
        .order_by("name")
    )

    labels, values = [], []

    for cat in categories:
        labels.append(cat.name)
        total = cat.total_stock_items or cat.total_product_stock or 0
        values.append(total)

    return labels, values


def get_chart_by_supplier():
    suppliers = (
        Supplier.objects
        .annotate(
            total_stock_items=Sum("products__stock_items__quantity"),
            total_product_stock=Sum("products__stock"),
        )
        .order_by("name")
    )

    labels, values = [], []

    for sup in suppliers:
        labels.append(sup.name)
        total = sup.total_stock_items or sup.total_product_stock or 0
        values.append(total)

    return labels, values


def get_chart_by_location():
    items = (
        StockItem.objects
        .values("location__name")
        .annotate(total=Sum("quantity"))
        .order_by("location__name")
    )

    labels = [row["location__name"] or "Sin ubicación" for row in items]
    values = [row["total"] or 0 for row in items]

    return labels, values


def get_chart_rotation_by_product():
    movements = (
        StockMovement.objects
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:10]
    )

    labels = [row["product__name"] or "Sin producto" for row in movements]
    values = [row["total"] or 0 for row in movements]

    return labels, values


def get_chart_movements_by_type():
    movements = (
        StockMovement.objects
        .values("movement_type")
        .annotate(total=Sum("quantity"))
        .order_by("movement_type")
    )

    labels = [row["movement_type"] or "Sin tipo" for row in movements]
    values = [row["total"] or 0 for row in movements]

    return labels, values