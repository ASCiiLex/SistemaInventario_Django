from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from .models import Supplier
from .forms import SupplierForm
from products.models import Product


def supplier_list(request):
    search = request.GET.get("q", "")
    suppliers = Supplier.objects.all()

    if search:
        suppliers = suppliers.filter(name__icontains=search)

    return render(request, "suppliers/list.html", {
        "suppliers": suppliers,
        "search": search,
    })


def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("supplier_list"))
    else:
        form = SupplierForm()

    return render(request, "suppliers/form.html", {
        "form": form,
        "title": "Nuevo Proveedor"
    })


def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect(reverse("supplier_list"))
    else:
        form = SupplierForm(instance=supplier)

    return render(request, "suppliers/form.html", {
        "form": form,
        "title": "Editar Proveedor"
    })


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect(reverse("supplier_list"))


def supplier_products(request, pk):
    products = (
        Product.objects
        .select_related("category")
        .filter(
            organization=request.organization,
            supplier_id=pk
        )
    )

    return render(request, "suppliers/partials/products.html", {
        "products": products
    })