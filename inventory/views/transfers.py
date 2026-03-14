from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from ..models import StockTransfer
from ..forms import (
    StockTransferCreateForm,
    StockTransferConfirmForm,
    StockTransferFilterForm,
)


def transfer_list(request):
    qs = StockTransfer.objects.select_related(
        "product", "origin", "destination", "created_by", "confirmed_by"
    ).all()

    filter_form = StockTransferFilterForm(request.GET or None)
    if filter_form.is_valid():
        product = filter_form.cleaned_data.get("product")
        origin = filter_form.cleaned_data.get("origin")
        destination = filter_form.cleaned_data.get("destination")
        status = filter_form.cleaned_data.get("status")

        if product:
            qs = qs.filter(product=product)
        if origin:
            qs = qs.filter(origin=origin)
        if destination:
            qs = qs.filter(destination=destination)
        if status:
            qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "transfers": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
    }

    if request.headers.get("HX-Request"):
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