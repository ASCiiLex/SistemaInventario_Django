from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F
from .models import Product
from categories.models import Category
from suppliers.models import Supplier
from .forms import ProductForm


def product_list(request):
    search = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    supplier_id = request.GET.get("supplier", "")
    stock_filter = request.GET.get("stock", "")  # all / low

    products = Product.objects.select_related("category", "supplier").all()

    if search:
        products = products.filter(name__icontains=search)

    if category_id:
        products = products.filter(category_id=category_id)

    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    if stock_filter == "low":
        products = products.filter(stock__lte=F("min_stock"))

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    context = {
        "products": products,
        "search": search,
        "category_id": category_id,
        "supplier_id": supplier_id,
        "stock_filter": stock_filter,
        "categories": categories,
        "suppliers": suppliers,
    }
    return render(request, "products/list.html", context)


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