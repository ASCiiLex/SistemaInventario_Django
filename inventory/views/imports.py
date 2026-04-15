from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

import csv

from ..forms.imports import StockImportForm
from ..utils.csv_importer import read_csv
from ..services.csv_import import (
    CSVImportValidator,
    CSVImportExecutor,
    NormalizedRow,
)

from inventory.services.audit import log_action
from inventory.models.imports import ImportJob
from inventory.models import Location


def download_template_view(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="stock_import_template.csv"'

    writer = csv.writer(response)
    writer.writerow(["sku", "name", "location", "stock_min", "stock_current"])

    return response


def import_stock_view(request):
    if request.method == "POST":
        form = StockImportForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                file = request.FILES["csv_file"]
                rows = read_csv(file)
            except Exception as e:
                messages.error(request, str(e))
                return redirect("import_stock")

            validator = CSVImportValidator(request.organization)
            validated, errors = validator.validate(rows)

            job = ImportJob.objects.create(
                organization=request.organization,
                user=request.user,
                file_name=file.name,
                status="preview",
                total_rows=len(rows),
                valid_rows=len(validated),
                error_rows=len(errors),
            )

            request.session["import_job_id"] = job.id

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
    job_id = request.session.get("import_job_id")

    if not validated_rows or errors or not job_id:
        messages.error(request, "Importación inválida.")
        return redirect("import_stock")

    try:
        job = ImportJob.objects.get(
            id=job_id,
            organization=request.organization
        )
    except ImportJob.DoesNotExist:
        messages.error(request, "Job no encontrado.")
        return redirect("import_stock")

    # 🔒 Protección estado
    if job.status == "completed":
        messages.info(request, "Este import ya fue ejecutado.")
        return redirect("import_stock")

    if job.status != "preview":
        messages.error(request, "Este import no está en estado válido.")
        return redirect("import_stock")

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

    try:
        job.status = "confirmed"
        job.save(update_fields=["status"])

        processed, report = executor.execute(reconstructed)

        job.status = "completed"
        job.executed_at = timezone.now()
        job.meta = {
            "summary": report["summary"],
            "source": {
                "filename": job.file_name,
                "user_agent": request.META.get("HTTP_USER_AGENT"),
            }
        }
        job.save(update_fields=["status", "executed_at", "meta"])

    except Exception as e:
        job.status = "failed"
        job.meta = {"error": str(e)}
        job.save(update_fields=["status", "meta"])
        raise

    log_action(
        request.user,
        "IMPORT",
        None,
        {
            "rows_processed": processed,
            "rows_total": len(validated_rows),
            "job_id": job.id,
        },
        organization=request.organization,
    )

    request.session.pop("import_validated", None)
    request.session.pop("import_errors", None)
    request.session.pop("import_job_id", None)

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