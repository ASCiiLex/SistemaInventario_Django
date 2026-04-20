from django.shortcuts import render

from dashboard.services.dashboard_metrics import (
    get_dashboard_metrics,
    get_low_stock,
)
from dashboard.services.observability_metrics import get_system_metrics
from accounts.permissions import can_view_system_metrics


def dashboard_totals(request):
    context = get_dashboard_metrics(request.organization)
    return render(request, "dashboard/partials/totals.html", context)


def dashboard_low_stock(request):
    low_stock = get_low_stock(request.organization)
    return render(
        request,
        "dashboard/partials/low_stock.html",
        {"low_stock": low_stock},
    )


def dashboard_system_metrics(request):
    if not can_view_system_metrics(request.user, request.organization):
        return render(request, "dashboard/partials/empty.html")

    context = get_system_metrics(request.organization)

    return render(
        request,
        "dashboard/partials/system_metrics.html",
        context,
    )