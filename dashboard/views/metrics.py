from django.shortcuts import render
from dashboard.services.metrics import (
    get_dashboard_metrics,
    get_low_stock,
    get_system_metrics,
)


def dashboard_totals(request):
    context = get_dashboard_metrics(request.organization)
    return render(request, "dashboard/partials/totals.html", context)


def dashboard_low_stock(request):
    low_stock = get_low_stock(request.organization)
    return render(request, "dashboard/partials/low_stock.html", {"low_stock": low_stock})


def dashboard_system_metrics(request):
    context = get_system_metrics(request.organization)
    return render(request, "dashboard/partials/system_metrics.html", context)