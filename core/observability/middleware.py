import time
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve

from .metrics import http_requests_total, http_request_duration_seconds, errors_total


class ObservabilityMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if not hasattr(request, "_start_time"):
            return response

        duration = time.time() - request._start_time

        method = request.method
        status = response.status_code

        try:
            match = resolve(request.path)
            endpoint = match.route or match.url_name or request.path
        except Exception:
            endpoint = request.path

        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response

    def process_exception(self, request, exception):
        errors_total.labels(type=exception.__class__.__name__).inc()
        return None