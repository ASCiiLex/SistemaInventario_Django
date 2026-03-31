import csv

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

from ..models import StockMovement
from ..forms import StockMovementForm, StockMovementFilterForm
from ..utils.listing import ListViewMixin
from notifications.utils import broadcast_notification


class StockMovementListView(ListViewMixin):
    allowed_sort_fields = [
        "created_at",
        "product__name",
        "movement_type",
        "origin__name",
        "destination__name",
        "quantity",
    ]
    default_ordering = "-created_at"

    def get_queryset(self, request):
        qs = StockMovement.objects.select_related(
            "product", "origin", "destination"
        ).all()

        filter_form = StockMovementFilterForm(request.GET or None)

        if filter_form.is_valid():
            data = filter_form.cleaned_data

            if data.get("product"):
                qs = qs.filter(product=data["product"])
            if data.get("movement_type"):
                qs = qs.filter(movement_type=data["movement_type"])
            if data.get("origin"):
                qs = qs.filter(origin=data["origin"])
            if data.get("destination"):
                qs = qs.filter(destination=data["destination"])
            if data.get("q"):
                qs = qs.filter(product__name__icontains=data["q"])
            if data.get("date_from"):
                qs = qs.filter(created_at__date__gte=data["date_from"])
            if data.get("date_to"):
                qs = qs.filter(created_at__date__lte=data["date_to"])

        qs = self.apply_ordering(request, qs)

        return qs, filter_form


def stockmovement_list(request):
    view = StockMovementListView()

    qs, filter_form = view.get_queryset(request)
    page_obj = view.paginate_queryset(request, qs)

    context = {
        "movements": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
        "current_sort": request.GET.get("sort", ""),
        "current_dir": request.GET.get("dir", "asc"),
    }

    if view.is_htmx(request):
        return render(request, "inventory/stock/partials/table.html", context)

    return render(request, "inventory/stock/list.html", context)


def stockmovement_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save()
            product = movement.product

            broadcast_notification(
                {
                    "type": "movement",
                    "message": "Nuevo movimiento registrado",
                    "product": product.name,
                }
            )

            view = StockMovementListView()
            qs, filter_form = view.get_queryset(request)
            page_obj = view.paginate_queryset(request, qs)

            context = {
                "movements": page_obj,
                "page_obj": page_obj,
                "filter_form": filter_form,
            }

            if view.is_htmx(request):
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