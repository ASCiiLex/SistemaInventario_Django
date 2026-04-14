from django.shortcuts import render, redirect
from django.contrib import messages

from ..forms.imports import StockImportForm
from ..utils.csv_importer import read_csv
from ..services.csv_import import validate_rows, execute_import

from inventory.services.audit import log_action


def import_stock_view(request):
    if request.method == "POST":
        form = StockImportForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            rows = read_csv(csv_file)

            validated, errors = validate_rows(rows, request.organization)

            request.session["import_validated"] = [
                {
                    "product_id": r["product"].id,
                    "location_id": r["location"].id,
                    "quantity": r["quantity"],
                }
                for r in validated
            ]

            request.session["import_errors"] = errors

            return render(
                request,
                "inventory/imports/preview.html",
                {
                    "rows": rows,
                    "errors": errors,
                    "valid_count": len(validated),
                    "error_count": len(errors),
                },
            )
    else:
        form = StockImportForm()

    return render(request, "inventory/imports/import.html", {"form": form})


def import_stock_confirm_view(request):
    validated_rows = request.session.get("import_validated")
    errors = request.session.get("import_errors", [])

    if not validated_rows:
        messages.error(request, "No hay datos válidos para importar.")
        return redirect("import_stock")

    if errors:
        messages.error(request, "No se puede importar: existen errores en el CSV.")
        return redirect("import_stock")

    from products.models import Product
    from inventory.models import Location

    reconstructed = []

    for row in validated_rows:
        try:
            product = Product.objects.get(
                id=row["product_id"],
                organization=request.organization
            )
            location = Location.objects.get(
                id=row["location_id"],
                organization=request.organization
            )

            reconstructed.append({
                "product": product,
                "location": location,
                "quantity": row["quantity"],
            })
        except Exception:
            continue

    processed = execute_import(reconstructed, request.organization)

    log_action(
        request.user,
        "IMPORT",
        None,
        {
            "rows_processed": processed,
            "rows_total": len(validated_rows),
        },
        organization=request.organization,
    )

    request.session.pop("import_validated", None)
    request.session.pop("import_errors", None)

    messages.success(
        request,
        f"Importación completada. {processed} filas procesadas."
    )

    return redirect("import_stock")