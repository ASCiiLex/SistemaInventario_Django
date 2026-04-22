from django.shortcuts import render
from observability.models import SlowRequest

from dashboard.services.observability_metrics import get_system_metrics
from accounts.permissions import can_view_system_metrics


def observability_dashboard_view(request):
    context = {}

    if can_view_system_metrics(request.user, request.organization):
        context = get_system_metrics(request.organization)

    return render(
        request,
        "observability/dashboard.html",
        context,
    )


def slow_requests_view(request):
    slow_requests = SlowRequest.objects.all()[:50]

    return render(
        request,
        "observability/slow_requests.html",
        {"slow_requests": slow_requests},
    )