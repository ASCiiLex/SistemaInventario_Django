from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F, IntegerField, Sum
from django.db.models.functions import Cast, Substr
from django.http import HttpResponse
from django.template.loader import render_to_string
import csv

from .models import Product
from categories.models import Category
from suppliers.models import Supplier
from .forms import ProductForm
from inventory.utils.listing import ListViewMixin


def product_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "name",
        "sku",
        "category__name",
        "supplier__name",
        "stock",
        "min_stock",
    ]
    view.default_ordering = "name"

    search = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    supplier_id = request.GET.get("supplier", "")
    stock_filter = request.GET.get("stock", "")

    products = Product.objects.select_related("category", "supplier").annotate(
        total_stock_db=Sum("stock_items__quantity"),
        total_min_stock_db=Sum("stock_items__min_stock"),
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

    sort = request.GET.get("sort", "")
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

    elif sort == "stock":
        order_field = "total_stock_db"

    elif sort == "min_stock":
        order_field = "total_min_stock_db"

    else:
        products = view.apply_ordering(request, products)
        order_field = None

    if order_field:
        if direction == "desc":
            order_field = f"-{order_field}"
        products = products.order_by(order_field)

    page_obj = view.paginate_queryset(request, products)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "search": search,
        "category_id": category_id,
        "supplier_id": supplier_id,
        "stock_filter": stock_filter,
        "categories": categories,
        "suppliers": suppliers,
        "current_sort": request.GET.get("sort", ""),
        "current_dir": request.GET.get("dir", "asc"),
    }

    if view.is_htmx(request):
        return render(request, "products/partials/products_table.html", context)

    return render(request, "products/list.html", context)


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

    for p in Product.objects.select_related("category", "supplier").all():
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


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/detail.html", {"product": product})


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("product_list"))
    else:
        form = ProductForm()

    return render(request, "products/form.html", {"form": form, "title": "Crear Producto"})


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect(reverse("product_list"))
    else:
        form = ProductForm(instance=product)

    return render(request, "products/form.html", {"form": form, "title": "Editar Producto"})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect(reverse("product_list"))


def lowstock_counter(request):
    count = Product.objects.annotate(
        total_stock_db=Sum("stock_items__quantity"),
        total_min_stock_db=Sum("stock_items__min_stock"),
    ).filter(
        total_stock_db__lte=F("total_min_stock_db")
    ).count()

    html = render_to_string(
        "products/partials/lowstock_counter.html",
        {"count": count}
    )

    return HttpResponse(html)


def stockitem_counter(request):
    from inventory.models import StockItem
    from django.db.models import F

    count = StockItem.objects.filter(
        quantity__lte=F("min_stock")
    ).count()

    html = render_to_string(
        "products/partials/stockitem_counter.html",
        {"count": count}
    )

    return HttpResponse(html)