from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Product
from .forms import ProductForm


def product_list(request):
    search = request.GET.get("q", "")

    products = Product.objects.all()

    if search:
        products = products.filter(name__icontains=search)

    context = {
        "products": products,
        "search": search,
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