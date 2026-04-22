import time
import uuid
import logging

from django.urls import resolve
from django.db import connection
from django.core.cache import cache

from core.security.errors import safe_log_error
from observability.models import SlowRequest

from .metrics import http_requests_total, http_request_duration_seconds, errors_total
from .tracing import set_trace_id, clear_trace, trace_db_query, get_trace_stats


logger = logging.getLogger("inventory.domain")


class ObservabilityMiddleware:

    SLOW_REQUEST_THRESHOLD = 0.5  # segundos

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        start_time = time.time()

        trace_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.trace_id = trace_id

        set_trace_id(trace_id)

        try:
            connection.execute_wrapper(trace_db_query)
        except Exception:
            pass

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

        # 🔥 DB (NO CRÍTICO)
        if duration >= self.SLOW_REQUEST_THRESHOLD:
            try:
                SlowRequest.objects.create(**trace_summary)
            except Exception:
                pass

        # 🔥 CACHE (NO CRÍTICO)
        try:
            cache_key = "observability:slow_requests"
            slow_requests = cache.get(cache_key, [])

            slow_requests.append(trace_summary)
            slow_requests = sorted(
                slow_requests,
                key=lambda x: x["total_time"],
                reverse=True
            )[:10]

            cache.set(cache_key, slow_requests, 60)
        except Exception:
            pass

        try:
            response["X-Request-ID"] = getattr(request, "trace_id", "")
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