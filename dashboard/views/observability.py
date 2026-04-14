from django.http import JsonResponse
from django.core.cache import cache


def slow_requests_view(request):
    data = cache.get("observability:slow_requests", [])

    return JsonResponse({
        "slow_requests": data
    })