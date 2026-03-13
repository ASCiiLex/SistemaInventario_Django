from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    Location,
    Order,
    StockMovement,
    StockItem,
    StockTransfer,   # NUEVO
)

from .forms import (
    StockMovementForm,
    StockTransferForm,
    StockImportForm,
    StockTransferCreateForm,   # NUEVO
    StockTransferConfirmForm,  # NUEVO
)

from .utils.csv_importer import read_csv
from products.models import Product


# ---------------------------------------------------------
# LISTADOS EXISTENTES
# ---------------------------------------------------------

def location_list(request):
    locations = Location.objects.all()
    return render(request, "inventory/location_list.html", {"locations": locations})


def order_list(request):
    orders = Order.objects.select_related("supplier", "location").all()
    return render(request, "inventory/order_list.html", {"orders": orders})


def stockmovement_list(request):
    movements = StockMovement.objects.select_related("product", "origin", "destination").all()
    return render(request, "inventory/stockmovement_list.html", {"movements": movements})


# ---------------------------------------------------------
# MOVIMIENTOS EXISTENTES
# ---------------------------------------------------------

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
        "inventory/stockmovement_form.html",
        {
            "form": form,
            "title": "Nuevo movimiento de stock",
        },
    )


def stock_transfer_create(request):
    if request.method == "POST":
        form = StockTransferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("stockmovement_list"))
    else:
        form = StockTransferForm()

    return render(
        request,
        "inventory/stock_transfer_form.html",
        {
            "form": form,
            "title": "Transferencia entre almacenes",
        },
    )


# ---------------------------------------------------------
# NUEVO — MÓDULO DE TRANSFERENCIAS PROFESIONALES
# ---------------------------------------------------------

@login_required
def transfer_list(request):
    transfers = StockTransfer.objects.select_related(
        "product", "origin", "destination", "created_by", "confirmed_by"
    ).all()

    return render(request, "inventory/transfer_list.html", {"transfers": transfers})


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
        "inventory/transfer_form.html",
        {"form": form, "title": "Nueva transferencia"},
    )


@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    return render(request, "inventory/transfer_detail.html", {"transfer": transfer})


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
        "inventory/transfer_confirm.html",
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


# ---------------------------------------------------------
# IMPORTACIÓN CSV — EXISTENTE
# ---------------------------------------------------------

def import_stock_view(request):
    if request.method == "POST":
        form = StockImportForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            rows = read_csv(csv_file)

            request.session["import_rows"] = rows

            return render(request, "inventory/import_stock_preview.html", {
                "rows": rows,
            })

    else:
        form = StockImportForm()

    return render(request, "inventory/import_stock.html", {"form": form})


def import_stock_confirm_view(request):
    rows = request.session.get("import_rows")

    if not rows:
        messages.error(request, "No hay datos para importar.")
        return redirect("import_stock")

    for row in rows:
        product_code = row.get("product_code")
        location_code = row.get("location_code")
        quantity = int(row.get("quantity", 0))

        try:
            product = Product.objects.get(code=product_code)
            location = Location.objects.get(code=location_code)
        except Exception:
            continue

        stock_item, created = StockItem.objects.get_or_create(
            product=product,
            location=location,
            defaults={"quantity": quantity},
        )

        if not created:
            stock_item.quantity = quantity
            stock_item.save()

    messages.success(request, "Stock importado correctamente.")
    return redirect("import_stock")