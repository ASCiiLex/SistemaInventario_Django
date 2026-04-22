from django.shortcuts import render, redirect
from django.urls import reverse

from products.forms import ProductForm
from accounts.permissions import can_create_products
from accounts.decorators import permission_required_custom


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