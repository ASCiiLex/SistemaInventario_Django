from django.http import JsonResponse
from observability.models import SlowRequest


def slow_requests_view(request):
    data = list(
        SlowRequest.objects
        .values(
            "trace_id",
            "endpoint",
            "method",
            "status",
            "total_time",
            "db_time",
            "db_queries",
            "slow_queries",
            "created_at",
        )[:50]
    )

    return JsonResponse({
        "slow_requests": data
    })