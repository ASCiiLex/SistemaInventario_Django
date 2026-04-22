from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from products.models import Product
from products.forms import ProductForm
from accounts.permissions import can_edit_products
from accounts.decorators import permission_required_custom


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