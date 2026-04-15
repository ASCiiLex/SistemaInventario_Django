from django.shortcuts import render, redirect
from django.contrib import messages

from ..forms.imports import StockImportForm
from ..utils.csv_importer import read_csv
from ..services.csv_import import CSVImportValidator, CSVImportExecutor, NormalizedRow

from inventory.services.audit import log_action


def import_stock_view(request):
    if request.method == "POST":
        form = StockImportForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                rows = read_csv(request.FILES["csv_file"])
            except Exception as e:
                messages.error(request, str(e))
                return redirect("import_stock")

            validator = CSVImportValidator(request.organization)
            validated, errors = validator.validate(rows)

            request.session["import_validated"] = [
                {
                    "sku": r.sku,
                    "name": r.name,
                    "location_id": r.location.id,
                    "stock_min": r.stock_min,
                    "stock_current": r.stock_current,
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

    if not validated_rows or errors:
        messages.error(request, "Importación inválida.")
        return redirect("import_stock")

    from inventory.models import Location

    reconstructed = []

    for row in validated_rows:
        try:
            location = Location.objects.get(
                id=row["location_id"],
                organization=request.organization
            )

            reconstructed.append(
                NormalizedRow(
                    sku=row["sku"],
                    name=row["name"],
                    location=location,
                    stock_min=row["stock_min"],
                    stock_current=row["stock_current"],
                )
            )
        except Exception:
            continue

    executor = CSVImportExecutor(request.organization, request.user)
    processed, report = executor.execute(reconstructed)

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

    messages.success(request, f"{processed} filas importadas.")

    return render(
        request,
        "inventory/imports/preview.html",
        {
            "rows": report["rows"],
            "errors": [],
            "valid_count": report["summary"]["processed"],
            "error_count": 0,
            "result_mode": True,
            "summary": report["summary"]
        }
    )