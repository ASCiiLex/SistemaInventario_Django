import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.db import connection
from django.core.cache import cache

from .metrics import http_requests_total, http_request_duration_seconds, errors_total
from .tracing import set_trace_id, clear_trace, trace_db_query, get_trace_stats


class ObservabilityMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request._start_time = time.time()

        trace_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.trace_id = trace_id

        set_trace_id(trace_id)

        connection.execute_wrapper(trace_db_query)

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

        # 🔥 TRACE SUMMARY
        stats = get_trace_stats()

        trace_summary = {
            "trace_id": getattr(request, "trace_id", ""),
            "endpoint": endpoint,
            "status": status,
            "total_time": round(duration, 4),
            "db_time": round(stats["db_time"], 4),
            "db_queries": stats["db_queries"],
            "slow_queries": stats["slow_queries"],
        }

        import logging
        logger = logging.getLogger("inventory.domain")
        logger.info("trace.summary", extra=trace_summary)

        # 🔥 TOP SLOW REQUESTS (cache)
        cache_key = "observability:slow_requests"
        slow_requests = cache.get(cache_key, [])

        slow_requests.append(trace_summary)
        slow_requests = sorted(slow_requests, key=lambda x: x["total_time"], reverse=True)[:10]

        cache.set(cache_key, slow_requests, 60)

        response["X-Request-ID"] = getattr(request, "trace_id", "")

        clear_trace()

        return response

    def process_exception(self, request, exception):
        errors_total.labels(type=exception.__class__.__name__).inc()
        return None