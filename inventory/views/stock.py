from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator

from ..models import StockMovement
from ..forms import StockMovementForm, StockMovementFilterForm


def stockmovement_list(request):
    qs = StockMovement.objects.select_related("product", "origin", "destination").all()

    filter_form = StockMovementFilterForm(request.GET or None)
    if filter_form.is_valid():
        product = filter_form.cleaned_data.get("product")
        movement_type = filter_form.cleaned_data.get("movement_type")
        origin = filter_form.cleaned_data.get("origin")
        destination = filter_form.cleaned_data.get("destination")

        if product:
            qs = qs.filter(product=product)
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if origin:
            qs = qs.filter(origin=origin)
        if destination:
            qs = qs.filter(destination=destination)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "movements": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
    }

    if request.headers.get("HX-Request"):
        return render(request, "inventory/stock/partials/table.html", context)

    return render(request, "inventory/stock/list.html", context)


def stockmovement_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("stockmovement_list"))
    else:
        form = StockMovementForm()

    return render(
        request,
        "inventory/stock/form.html",
        {"form": form, "title": "Nuevo movimiento de stock"},
    )