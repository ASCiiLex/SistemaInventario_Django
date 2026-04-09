from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F, IntegerField, Sum, Value
from django.db.models.functions import Cast, Substr, Coalesce
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
import csv

from .models import Product
from categories.models import Category
from suppliers.models import Supplier
from .forms import ProductForm
from inventory.utils.listing import ListViewMixin

# 🔐 PERMISSIONS
from accounts.permissions import (
    can_create_products,
    can_edit_products,
    can_delete_products,
    can_export_products,
)
from accounts.decorators import permission_required_custom


# ==========================================
# LIST
# ==========================================

def product_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "name",
        "sku",
        "category__name",
        "supplier__name",
        "total_stock_db",
        "total_min_stock_db",
    ]
    view.default_ordering = "name"

    search = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    supplier_id = request.GET.get("supplier", "")
    stock_filter = request.GET.get("stock", "")

    products = (
        Product.objects
        .select_related("category", "supplier")
        .filter(organization=request.organization)
        .annotate(
            total_stock_db=Coalesce(Sum("stock_items__quantity"), Value(0)),
            total_min_stock_db=Coalesce(Sum("stock_items__min_stock"), Value(0)),
        )
    )

    if search:
        products = products.filter(name__icontains=search)

    if category_id:
        products = products.filter(category_id=category_id)

    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    if stock_filter == "low":
        products = products.filter(
            total_stock_db__lte=F("total_min_stock_db")
        )

    sort = request.GET.get("sort")
    direction = request.GET.get("dir", "asc")

    if sort == "sku":
        products = products.annotate(
            sku_number=Cast(Substr("sku", 4), IntegerField())
        )
        order_field = "sku_number"

    elif sort == "name":
        products = products.annotate(
            name_number=Cast(Substr("name", 9), IntegerField())
        )
        order_field = "name_number"

    elif sort in ["total_stock_db", "total_min_stock_db"]:
        order_field = sort

    else:
        products = view.apply_ordering(request, products)
        order_field = None

    if order_field:
        if direction == "desc":
            order_field = f"-{order_field}"
        products = products.order_by(order_field)

    page_obj = view.paginate_queryset(request, products)

    category_name = None
    supplier_name = None

    if category_id:
        category = Category.objects.filter(
            id=category_id,
            organization=request.organization
        ).first()
        if category:
            category_name = category.name

    if supplier_id:
        supplier = Supplier.objects.filter(
            id=supplier_id,
            organization=request.organization
        ).first()
        if supplier:
            supplier_name = supplier.name

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "search": search,
        "category_id": category_id,
        "supplier_id": supplier_id,
        "stock_filter": stock_filter,
        "category_name": category_name,
        "supplier_name": supplier_name,
        **view.get_ordering_context(request),
    }

    if view.is_htmx(request):
        return render(request, "products/partials/products_table.html", context)

    return render(request, "products/list.html", context)


# ==========================================
# EXPORT
# ==========================================

@permission_required_custom(can_export_products)
def export_products_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=productos.csv"

    writer = csv.writer(response)
    writer.writerow([
        "Nombre",
        "SKU",
        "Categoría",
        "Proveedor",
        "Stock",
        "Mínimo",
        "Coste",
        "Precio venta",
        "Margen",
        "Valor inventario",
    ])

    for p in Product.objects.select_related("category", "supplier").filter(
        organization=request.organization
    ):
        writer.writerow([
            p.name,
            p.sku,
            p.category.name if p.category else "",
            p.supplier.name if p.supplier else "",
            p.total_stock,
            p.total_min_stock,
            f"{p.cost_price:.2f}",
            f"{p.sale_price:.2f}",
            f"{p.margin:.2f}",
            f"{p.inventory_value:.2f}",
        ])

    return response


# ==========================================
# DETAIL
# ==========================================

def product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        organization=request.organization
    )
    return render(request, "products/detail.html", {"product": product})


# ==========================================
# CREATE
# ==========================================

@permission_required_custom(can_create_products)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            organization=request.organization
        )
        if form.is_valid():
            form.save()
            return redirect(reverse("product_list"))
    else:
        form = ProductForm(organization=request.organization)

    return render(request, "products/form.html", {
        "form": form,
        "title": "Crear Producto"
    })


# ==========================================
# EDIT
# ==========================================

@permission_required_custom(can_edit_products)
def product_edit(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        organization=request.organization
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
            organization=request.organization
        )
        if form.is_valid():
            form.save()
            return redirect(reverse("product_list"))
    else:
        form = ProductForm(
            instance=product,
            organization=request.organization
        )

    return render(request, "products/form.html", {
        "form": form,
        "title": "Editar Producto"
    })


# ==========================================
# DELETE
# ==========================================

@permission_required_custom(can_delete_products)
def product_delete(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        organization=request.organization
    )
    product.delete()
    return redirect(reverse("product_list"))


# ==========================================
# COUNTERS
# ==========================================

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
    from inventory.models import StockItem

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


# ==========================================
# AJAX
# ==========================================

def ajax_categories(request):
    q = request.GET.get("q", "")

    qs = Category.objects.filter(
        organization=request.organization
    )

    if q:
        qs = qs.filter(name__icontains=q)

    data = [
        {"id": c.id, "text": c.name}
        for c in qs.order_by("name")[:20]
    ]

    return JsonResponse({"results": data})


def ajax_suppliers(request):
    q = request.GET.get("q", "")

    qs = Supplier.objects.filter(
        organization=request.organization
    )

    if q:
        qs = qs.filter(name__icontains=q)

    data = [
        {"id": s.id, "text": s.name}
        for s in qs.order_by("name")[:20]
    ]

    return JsonResponse({"results": data})