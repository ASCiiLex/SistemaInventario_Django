from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Category
from .forms import CategoryForm
from products.models import Product


def category_list(request):
    search = request.GET.get("q", "")
    categories = Category.objects.all()

    if search:
        categories = categories.filter(name__icontains=search)

    return render(request, "categories/list.html", {
        "categories": categories,
        "search": search,
    })


def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("category_list"))
    else:
        form = CategoryForm()

    return render(request, "categories/form.html", {
        "form": form,
        "title": "Nueva Categoría"
    })


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect(reverse("category_list"))
    else:
        form = CategoryForm(instance=category)

    return render(request, "categories/form.html", {
        "form": form,
        "title": "Editar Categoría"
    })


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect(reverse("category_list"))


def category_products(request, pk):
    products = (
        Product.objects
        .select_related("supplier")
        .filter(
            organization=request.organization,
            category_id=pk
        )
    )

    return render(request, "categories/partials/products.html", {
        "products": products
    })