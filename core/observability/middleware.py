import time
from django.utils.deprecation import MiddlewareMixin
from .metrics import http_requests_total, http_request_duration_seconds, errors_total


class ObservabilityMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if not hasattr(request, "_start_time"):
            return response

        duration = time.time() - request._start_time

        method = request.method
        path = request.path
        status = response.status_code

        http_requests_total.labels(
            method=method,
            endpoint=path,
            status=status
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=path
        ).observe(duration)

        return response

    def process_exception(self, request, exception):
        errors_total.labels(type=exception.__class__.__name__).inc()
        return None