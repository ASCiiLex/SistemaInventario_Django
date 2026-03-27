from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import JsonResponse

from products.models import Product
from suppliers.models import Supplier
from categories.models import Category
from inventory.models import StockItem, StockMovement
from notifications.models import Notification


def dashboard_view(request):
    total_stock_real = StockItem.objects.aggregate(total=Sum("quantity"))["total"]
    if total_stock_real is None:
        total_stock_real = Product.objects.aggregate(total=Sum("stock"))["total"] or 0

    low_stock_list = _get_low_stock_products()
    low_stock_count = len(low_stock_list)

    categories = (
        Category.objects
        .annotate(
            total_stock_items=Sum("products__stock_items__quantity"),
            total_product_stock=Sum("products__stock"),
        )
        .order_by("name")
    )

    chart_labels = []
    chart_values = []

    for cat in categories:
        chart_labels.append(cat.name)
        total = cat.total_stock_items
        if total is None:
            total = cat.total_product_stock or 0
        chart_values.append(total)

    # -------------------------
    # FIX NOTIFICATIONS SUMMARY
    # -------------------------
    notifications_total = Notification.objects.count()
    notifications_unread = Notification.objects.filter(seen=False).count()
    notifications_by_type = (
        Notification.objects
        .values("type")
        .annotate(total=Count("id"))
    )

    context = {
        "total_products": Product.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": total_stock_real,
        "low_stock_count": low_stock_count,
        "chart_labels": chart_labels,
        "chart_values": chart_values,

        # FIX
        "notifications_total": notifications_total,
        "notifications_unread": notifications_unread,
        "notifications_by_type": notifications_by_type,
    }

    return render(request, "dashboard/dashboard.html", context)


# ============================================
# HELPERS
# ============================================

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
                    "product": p,
                    "quantity": current_stock,
                    "min_stock": p.min_stock,
                }
            )

    return low_stock


# ============================================
# PARTIALS
# ============================================

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


def dashboard_notifications_recent(request):
    notifications = Notification.objects.order_by("-created_at")[:10]

    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": notifications},
    )


def dashboard_recent_movements(request):
    recent_movements = (
        StockMovement.objects
        .select_related("product", "origin", "destination")
        .exclude(origin__isnull=True, destination__isnull=True)  # FIX
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "dashboard/partials/recent_movements.html",
        {"movements": recent_movements},
    )


def dashboard_recent_stock_movements(request):
    recent_stock_movements = (
        StockMovement.objects
        .select_related("product")
        .order_by("-created_at")
    )

    return render(
        request,
        "dashboard/partials/recent_stock_movements.html",
        {"stock_movements": recent_stock_movements},
    )


# ============================================
# CHARTS
# ============================================

def _get_chart_by_category():
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

    return labels, values


def _get_chart_by_supplier():
    suppliers = (
        Supplier.objects
        .annotate(
            total_stock_items=Sum("products__stock_items__quantity"),
            total_product_stock=Sum("products__stock"),
        )
        .order_by("name")
    )

    labels = []
    values = []

    for sup in suppliers:
        labels.append(sup.name)
        total = sup.total_stock_items
        if total is None:
            total = sup.total_product_stock or 0
        values.append(total)

    return labels, values


def _get_chart_by_location():
    items = (
        StockItem.objects
        .values("location__name")
        .annotate(total=Sum("quantity"))
        .order_by("location__name")
    )

    labels = []
    values = []

    for row in items:
        labels.append(row["location__name"] or "Sin ubicación")
        values.append(row["total"] or 0)

    return labels, values


def _get_chart_rotation_by_product():
    movements = (
        StockMovement.objects
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:10]
    )

    labels = []
    values = []

    for row in movements:
        labels.append(row["product__name"] or "Sin producto")
        values.append(row["total"] or 0)

    return labels, values


def _get_chart_movements_by_type():
    movements = (
        StockMovement.objects
        .values("movement_type")
        .annotate(total=Sum("quantity"))
        .order_by("movement_type")
    )

    labels = []
    values = []

    for row in movements:
        labels.append(row["movement_type"] or "Sin tipo")
        values.append(row["total"] or 0)

    return labels, values


def dashboard_chart(request):
    labels, values = _get_chart_by_category()

    context = {
        "chart_labels": labels,
        "chart_values": values,
    }

    return render(request, "dashboard/partials/chart.html", context)


def dashboard_chart_data(request, tipo):
    if tipo == "categorias":
        labels, values = _get_chart_by_category()
    elif tipo == "proveedores":
        labels, values = _get_chart_by_supplier()
    elif tipo == "almacenes":
        labels, values = _get_chart_by_location()
    elif tipo == "rotacion":
        labels, values = _get_chart_rotation_by_product()
    elif tipo == "movimientos":
        labels, values = _get_chart_movements_by_type()
    else:
        labels, values = [], []

    return JsonResponse({"labels": labels, "values": values})