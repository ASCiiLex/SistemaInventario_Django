from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F
from django.http import HttpResponse
import csv

from .models import Product
from categories.models import Category
from suppliers.models import Supplier
from .forms import ProductForm
from inventory.utils.listing import ListViewMixin


def product_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "name", "sku", "stock", "min_stock", "category__name", "supplier__name",
    ]
    view.default_ordering = "name"

    search = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    supplier_id = request.GET.get("supplier", "")
    stock_filter = request.GET.get("stock", "")

    products = Product.objects.select_related("category", "supplier").all()

    if search:
        products = products.filter(name__icontains=search)

    if category_id:
        products = products.filter(category_id=category_id)

    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    if stock_filter == "low":
        products = products.filter(stock__lte=F("min_stock"))

    # 🔥 ORDENACIÓN
    products = view.apply_ordering(request, products)

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
            p.min_stock,
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