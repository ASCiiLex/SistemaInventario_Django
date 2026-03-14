import csv

from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import HttpResponse

from ..models import StockMovement
from ..forms import StockMovementForm, StockMovementFilterForm
from notifications.utils import broadcast_notification

def _filtered_stockmovements(request):
    qs = StockMovement.objects.select_related("product", "origin", "destination").all()
    filter_form = StockMovementFilterForm(request.GET or None)

    if filter_form.is_valid():
        product = filter_form.cleaned_data.get("product")
        movement_type = filter_form.cleaned_data.get("movement_type")
        origin = filter_form.cleaned_data.get("origin")
        destination = filter_form.cleaned_data.get("destination")
        q = filter_form.cleaned_data.get("q")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")

        if product:
            qs = qs.filter(product=product)
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if origin:
            qs = qs.filter(origin=origin)
        if destination:
            qs = qs.filter(destination=destination)
        if q:
            qs = qs.filter(product__name__icontains=q)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

    return qs, filter_form

def stockmovement_list(request):
    qs, filter_form = _filtered_stockmovements(request)

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
            movement = form.save()
            product = movement.product

            if hasattr(product, "create_low_stock_notification"):
                product.create_low_stock_notification()

            broadcast_notification(
                {
                    "type": "movement",
                    "message": "Nuevo movimiento registrado",
                    "product": product.name,
                }
            )

            if request.headers.get("HX-Request"):
                qs, filter_form = _filtered_stockmovements(request)
                paginator = Paginator(qs, 25)
                page_number = request.GET.get("page")
                page_obj = paginator.get_page(page_number)

                context = {
                    "movements": page_obj,
                    "page_obj": page_obj,
                    "filter_form": filter_form,
                }

                response = render(
                    request,
                    "inventory/stock/partials/table.html",
                    context,
                )
                response[
                    "HX-Trigger"
                ] = '{"movement-created": {"message": "Movimiento creado correctamente"}}'
                return response

            return redirect(reverse("stockmovement_list"))
    else:
        form = StockMovementForm()

    if request.headers.get("HX-Request"):
        return render(
            request,
            "inventory/stock/partials/form_modal.html",
            {"form": form, "title": "Nuevo movimiento de stock"},
        )

    return render(
        request,
        "inventory/stock/form.html",
        {"form": form, "title": "Nuevo movimiento de stock"},
    )

def export_stockmovements_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=movimientos_stock.csv"

    writer = csv.writer(response)
    writer.writerow(["Producto", "Tipo", "Origen", "Destino", "Cantidad", "Fecha"])

    for m in StockMovement.objects.select_related("product", "origin", "destination").all():
        writer.writerow(
            [
                m.product.name,
                m.get_movement_type_display(),
                m.origin.name if m.origin else "-",
                m.destination.name if m.destination else "-",
                m.quantity,
                m.created_at.strftime("%d/%m/%Y %H:%M"),
            ]
        )

    return response