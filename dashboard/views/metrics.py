from django.shortcuts import render
from dashboard.services.metrics import get_system_metrics


def dashboard_system_metrics(request):
    context = get_system_metrics(request.organization)
    return render(request, "dashboard/partials/system_metrics.html", context)