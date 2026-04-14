from django.http import JsonResponse

from .rate_limit import RateLimiter
from .timeout import TimeoutException
from .cache_safety import SafeCache


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        self.rules = [
            ("POST:/inventory/stock", ["POST"], 10, 10),
            ("POST:/inventory/", ["POST"], 20, 10),
            ("GET:/dashboard", ["GET"], 60, 10),
        ]

    def __call__(self, request):

        identifier = self._get_identifier(request)

        for prefix, methods, limit, window in self.rules:
            if request.method in methods and request.path.startswith(prefix.split(":")[1]):

                limiter = RateLimiter(prefix, limit, window)

                if not limiter.is_allowed(identifier):
                    return JsonResponse(
                        {"error": "Rate limit exceeded"},
                        status=429
                    )

        try:
            response = self.get_response(request)

            SafeCache.enforce_limits()

            return response

        except TimeoutException:
            return JsonResponse(
                {"error": "Request timeout"},
                status=504
            )

    def _get_identifier(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            return f"user:{user.id}"

        return f"ip:{self._get_ip(request)}"

    def _get_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0]
        return request.META.get("REMOTE_ADDR")