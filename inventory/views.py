from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from .models import Location, Order, StockMovement, StockItem
from .forms import StockMovementForm, StockTransferForm, StockImportForm
from .utils.csv_importer import read_csv
from products.models import Product


def location_list(request):
    locations = Location.objects.all()
    return render(request, "inventory/location_list.html", {"locations": locations})


def order_list(request):
    orders = Order.objects.select_related("supplier", "location").all()
    return render(request, "inventory/order_list.html", {"orders": orders})


def stockmovement_list(request):
    movements = StockMovement.objects.select_related("product", "origin", "destination").all()
    return render(request, "inventory/stockmovement_list.html", {"movements": movements})


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


# --------------------------------------------------------------------
# NUEVO: Importación CSV de stock inicial
# --------------------------------------------------------------------

def import_stock_view(request):
    if request.method == "POST":
        form = StockImportForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            rows = read_csv(csv_file)

            # Guardamos temporalmente en sesión
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
        # Ajustaremos el mapeo cuando tengas el CSV real
        product_code = row.get("product_code")
        location_code = row.get("location_code")
        quantity = int(row.get("quantity", 0))

        try:
            product = Product.objects.get(code=product_code)
            location = Location.objects.get(code=location_code)
        except Exception:
            continue  # ignoramos filas inválidas

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