from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import StockTransfer
from ..forms import (
    StockTransferCreateForm,
    StockTransferConfirmForm,
    StockTransferFilterForm,
)
from ..utils.listing import ListViewMixin

from accounts.permissions import (
    can_create_inventory,
    can_confirm_inventory,
)
from accounts.decorators import permission_required_custom


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

    qs = (
        StockTransfer.objects
        .select_related("product", "origin", "destination", "created_by", "confirmed_by")
        .filter(organization=request.organization)
    )

    filter_form = StockTransferFilterForm(
        request.GET or None,
        organization=request.organization
    )

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


@permission_required_custom(can_create_inventory)
def transfer_create(request):
    if request.method == "POST":
        form = StockTransferCreateForm(
            request.POST,
            organization=request.organization
        )

        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user
            transfer.save()

            messages.success(request, "Transferencia creada correctamente.")
            return redirect("transfer_list")
    else:
        form = StockTransferCreateForm(organization=request.organization)

    return render(
        request,
        "inventory/transfers/form.html",
        {"form": form, "title": "Nueva transferencia"},
    )


def transfer_detail(request, pk):
    transfer = get_object_or_404(
        StockTransfer,
        pk=pk,
        organization=request.organization
    )
    return render(request, "inventory/transfers/detail.html", {"transfer": transfer})


@permission_required_custom(can_confirm_inventory)
def transfer_confirm(request, pk):
    transfer = get_object_or_404(
        StockTransfer,
        pk=pk,
        organization=request.organization
    )

    if request.method == "POST":
        form = StockTransferConfirmForm(request.POST)
        if form.is_valid():
            transfer.confirm(request.user)

            messages.success(request, "Transferencia confirmada correctamente.")
            return redirect("transfer_detail", pk=pk)
    else:
        form = StockTransferConfirmForm()

    return render(
        request,
        "inventory/transfers/confirm.html",
        {"transfer": transfer, "form": form},
    )


@permission_required_custom(can_confirm_inventory)
def transfer_cancel(request, pk):
    transfer = get_object_or_404(
        StockTransfer,
        pk=pk,
        organization=request.organization
    )

    transfer.cancel(request.user)

    messages.success(request, "Transferencia cancelada correctamente.")
    return redirect("transfer_detail", pk=pk)