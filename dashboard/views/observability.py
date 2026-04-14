from django.shortcuts import render
from observability.models import SlowRequest


def slow_requests_view(request):
    slow_requests = SlowRequest.objects.all()[:50]

    return render(
        request,
        "dashboard/observability/slow_requests.html",
        {"slow_requests": slow_requests},
    )