from django.shortcuts import render
from django.db.models import Sum, F
from products.models import Product
from suppliers.models import Supplier
from categories.models import Category
from movements.models import Movement


def dashboard_view(request):
    # Productos bajo mínimo
    low_stock = Product.objects.filter(stock__lte=F("min_stock"))

    # Totales
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_stock = Product.objects.aggregate(total=Sum("stock"))["total"] or 0

    # Movimientos recientes
    recent_movements = (
        Movement.objects.select_related("product")
        .order_by("-created_at")[:10]
    )

    # Datos para gráfico: stock por categoría (optimizado)
    categories = (
        Category.objects
        .annotate(total_stock=Sum("products__stock"))
        .order_by("name")
    )

    chart_labels = [cat.name for cat in categories]
    chart_values = [cat.total_stock or 0 for cat in categories]

    context = {
        "low_stock": low_stock,
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_stock": total_stock,
        "recent_movements": recent_movements,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }

    return render(request, "dashboard/dashboard.html", context)