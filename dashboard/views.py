from django.shortcuts import render
from django.db.models import Sum
from products.models import Product
from suppliers.models import Supplier
from categories.models import Category
from movements.models import Movement
from inventory.models import StockItem, StockMovement


def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")


def _get_real_stock_for_product(product):
    qty = product.stock_items.aggregate(total=Sum("quantity"))["total"]
    if qty is None:
        return product.stock or 0
    return qty


def _get_low_stock_products():
    low_stock = []
    products = Product.objects.all().prefetch_related("stock_items")

    for p in products:
        current_stock = _get_real_stock_for_product(p)
        if current_stock <= (p.min_stock or 0):
            low_stock.append(
                {
                    "name": p.name,
                    "stock": current_stock,
                    "min_stock": p.min_stock,
                }
            )

    return low_stock


def dashboard_totals(request):
    total_stock_real = StockItem.objects.aggregate(total=Sum("quantity"))["total"]
    if total_stock_real is None:
        total_stock_real = Product.objects.aggregate(total=Sum("stock"))["total"] or 0

    low_stock_list = _get_low_stock_products()
    low_stock_count = len(low_stock_list)

    context = {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": total_stock_real,
        "low_stock_count": low_stock_count,
    }
    return render(request, "dashboard/partials/totals.html", context)


def dashboard_low_stock(request):
    low_stock = _get_low_stock_products()
    return render(request, "dashboard/partials/low_stock.html", {"low_stock": low_stock})


def dashboard_recent_movements(request):
    recent_movements = (
        Movement.objects.select_related("product")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "dashboard/partials/recent_movements.html",
        {"recent_movements": recent_movements},
    )


def dashboard_recent_stock_movements(request):
    recent_stock_movements = (
        StockMovement.objects.select_related("product", "origin", "destination")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "dashboard/partials/recent_stock_movements.html",
        {"recent_stock_movements": recent_stock_movements},
    )


def dashboard_chart(request):
    categories = (
        Category.objects
        .annotate(
            total_stock_items=Sum("products__stock_items__quantity"),
            total_product_stock=Sum("products__stock"),
        )
        .order_by("name")
    )

    labels = []
    values = []

    for cat in categories:
        labels.append(cat.name)
        total = cat.total_stock_items
        if total is None:
            total = cat.total_product_stock or 0
        values.append(total)

    context = {
        "chart_labels": labels,
        "chart_values": values,
    }

    return render(request, "dashboard/partials/chart.html", context)