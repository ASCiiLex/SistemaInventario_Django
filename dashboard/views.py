from django.shortcuts import render
from django.db.models import Sum, F
from products.models import Product
from suppliers.models import Supplier
from categories.models import Category
from movements.models import Movement


def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")


# BLOQUE: Totales
def dashboard_totals(request):
    context = {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": Product.objects.aggregate(total=Sum("stock"))["total"] or 0,
        "low_stock_count": Product.objects.filter(stock__lte=F("min_stock")).count(),
    }
    return render(request, "dashboard/partials/totals.html", context)


# BLOQUE: Productos bajo mínimo
def dashboard_low_stock(request):
    low_stock = Product.objects.filter(stock__lte=F("min_stock"))
    return render(request, "dashboard/partials/low_stock.html", {"low_stock": low_stock})


# BLOQUE: Movimientos recientes
def dashboard_recent_movements(request):
    recent_movements = (
        Movement.objects.select_related("product")
        .order_by("-created_at")[:10]
    )
    return render(request, "dashboard/partials/recent_movements.html", {
        "recent_movements": recent_movements
    })


# BLOQUE: Gráfico stock por categoría
def dashboard_chart(request):
    categories = (
        Category.objects
        .annotate(total_stock=Sum("products__stock"))
        .order_by("name")
    )

    context = {
        "chart_labels": [cat.name for cat in categories],
        "chart_values": [cat.total_stock or 0 for cat in categories],
    }

    return render(request, "dashboard/partials/chart.html", context)