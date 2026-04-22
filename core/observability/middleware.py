# core/observability/middleware.py

import time
import uuid
import logging

from django.urls import resolve

from core.security.errors import safe_log_error

from .metrics import http_requests_total, http_request_duration_seconds, errors_total
from .tracing import set_trace_id, clear_trace, get_trace_stats


logger = logging.getLogger("inventory.domain")


class ObservabilityMiddleware:

    SLOW_REQUEST_THRESHOLD = 0.5  # segundos

    EXCLUDED_PATHS = [
        "/login",
        "/static/",
        "/media/",
        "/favicon.ico",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path

        # 🔥 CRÍTICO: NO aplicar observabilidad en login y recursos básicos
        if any(path.startswith(p) for p in self.EXCLUDED_PATHS):
            return self.get_response(request)

        start_time = time.time()

        trace_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.trace_id = trace_id

        set_trace_id(trace_id)

        try:
            response = self.get_response(request)
        except Exception as e:
            self._handle_exception(request, e)
            raise

        duration = time.time() - start_time

        self._process_observability(request, response, duration)

        clear_trace()

        return response

    def _process_observability(self, request, response, duration):

        method = request.method
        status = response.status_code

        try:
            match = resolve(request.path)
            endpoint = match.route or match.url_name or request.path
        except Exception:
            endpoint = request.path

        try:
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
        except Exception:
            pass

        stats = get_trace_stats()

        trace_summary = {
            "trace_id": getattr(request, "trace_id", ""),
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "total_time": round(duration, 4),
            "db_time": round(stats.get("db_time", 0), 4),
            "db_queries": stats.get("db_queries", 0),
            "slow_queries": stats.get("slow_queries", 0),
        }

        try:
            logger.info("trace.summary", extra=trace_summary)
        except Exception:
            pass

    def _handle_exception(self, request, exception):
        try:
            errors_total.labels(type=exception.__class__.__name__).inc()

            safe_log_error(
                error_type=exception.__class__.__name__,
                message=str(exception),
                context=request.path
            )
        except Exception:
            pass