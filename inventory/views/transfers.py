from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import StockTransfer
from ..forms import StockTransferCreateForm, StockTransferConfirmForm


@login_required
def transfer_list(request):
    transfers = StockTransfer.objects.select_related(
        "product", "origin", "destination", "created_by", "confirmed_by"
    ).all()

    return render(request, "inventory/transfers/list.html", {"transfers": transfers})


@login_required
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


@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    return render(request, "inventory/transfers/detail.html", {"transfer": transfer})


@login_required
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


@login_required
def transfer_cancel(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)

    if transfer.status != "pending":
        messages.error(request, "Esta transferencia no se puede cancelar.")
        return redirect("transfer_detail", pk=pk)

    transfer.cancel(request.user)
    messages.success(request, "Transferencia cancelada correctamente.")
    return redirect("transfer_detail", pk=pk)