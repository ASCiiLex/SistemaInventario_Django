from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import StockTransfer
from ..forms import (
    StockTransferCreateForm,
    StockTransferConfirmForm,
    StockTransferFilterForm,
)
from ..utils.listing import ListViewMixin


def transfer_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "id",
        "product__name",
        "origin__name",
        "destination__name",
        "quantity",
        "status",
        "created_at",
    ]
    view.default_ordering = "-created_at"

    qs = StockTransfer.objects.select_related(
        "product", "origin", "destination", "created_by", "confirmed_by"
    ).all()

    filter_form = StockTransferFilterForm(request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        if data.get("product"):
            qs = qs.filter(product=data["product"])
        if data.get("origin"):
            qs = qs.filter(origin=data["origin"])
        if data.get("destination"):
            qs = qs.filter(destination=data["destination"])
        if data.get("status"):
            qs = qs.filter(status=data["status"])

    # 🔥 ORDENACIÓN
    qs = view.apply_ordering(request, qs)

    page_obj = view.paginate_queryset(request, qs)

    context = {
        "transfers": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
        "current_sort": request.GET.get("sort", ""),
        "current_dir": request.GET.get("dir", "asc"),
    }

    if view.is_htmx(request):
        return render(request, "inventory/transfers/partials/table.html", context)

    return render(request, "inventory/transfers/list.html", context)

def transfer_create(request):
    if request.method == "POST":
        form = StockTransferCreateForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user
            transfer.save()
            messages.success(request, "Transferencia creada correctamente.")
            return redirect("transfer_list")
    else:
        form = StockTransferCreateForm()

    return render(
        request,
        "inventory/transfers/form.html",
        {"form": form, "title": "Nueva transferencia"},
    )


def transfer_detail(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    return render(request, "inventory/transfers/detail.html", {"transfer": transfer})


def transfer_confirm(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)

    if transfer.status != "pending":
        messages.error(request, "Esta transferencia no se puede confirmar.")
        return redirect("transfer_detail", pk=pk)

    if request.method == "POST":
        form = StockTransferConfirmForm(request.POST)
        if form.is_valid():
            try:
                transfer.confirm(request.user)
                messages.success(request, "Transferencia confirmada correctamente.")
            except Exception as e:
                messages.error(request, str(e))
            return redirect("transfer_detail", pk=pk)
    else:
        form = StockTransferConfirmForm()

    return render(
        request,
        "inventory/transfers/confirm.html",
        {"transfer": transfer, "form": form},
    )


def transfer_cancel(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)

    if transfer.status != "pending":
        messages.error(request, "Esta transferencia no se puede cancelar.")
        return redirect("transfer_detail", pk=pk)

    transfer.cancel(request.user)
    messages.success(request, "Transferencia cancelada correctamente.")
    return redirect("transfer_detail", pk=pk)