from django.shortcuts import render, redirect
from django.contrib import messages

from ..forms import StockImportForm
from ..utils.csv_importer import read_csv
from ..models import StockItem, Location
from products.models import Product

from inventory.services.audit import log_action


def import_stock_view(request):
    if request.method == "POST":
        form = StockImportForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            rows = read_csv(csv_file)

            request.session["import_rows"] = rows

            return render(request, "inventory/imports/preview.html", {"rows": rows})

    else:
        form = StockImportForm()

    return render(request, "inventory/imports/import.html", {"form": form})


def import_stock_confirm_view(request):
    rows = request.session.get("import_rows")

    if not rows:
        messages.error(request, "No hay datos para importar.")
        return redirect("import_stock")

    total = 0

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

        total += 1

    log_action(
        request.user,
        "IMPORT",
        stock_item if total else None,
        {"rows_processed": total},
    )

    messages.success(request, "Stock importado correctamente.")
    return redirect("import_stock")