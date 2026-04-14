import time
import threading
from contextlib import contextmanager

_thread_locals = threading.local()


def set_trace_id(trace_id):
    _thread_locals.trace_id = trace_id
    _thread_locals.db_time = 0
    _thread_locals.db_queries = 0
    _thread_locals.slow_queries = 0


def get_trace_id():
    return getattr(_thread_locals, "trace_id", None)


def get_trace_stats():
    return {
        "db_time": getattr(_thread_locals, "db_time", 0),
        "db_queries": getattr(_thread_locals, "db_queries", 0),
        "slow_queries": getattr(_thread_locals, "slow_queries", 0),
    }


def clear_trace():
    _thread_locals.trace_id = None
    _thread_locals.current_span = None
    _thread_locals.db_time = 0
    _thread_locals.db_queries = 0
    _thread_locals.slow_queries = 0


def _set_current_span(span):
    _thread_locals.current_span = span


def _get_current_span():
    return getattr(_thread_locals, "current_span", None)


@contextmanager
def trace(span_name: str):
    start = time.time()

    parent = _get_current_span()
    _set_current_span(span_name)

    try:
        yield
    finally:
        duration = time.time() - start

        import logging
        logger = logging.getLogger("inventory.domain")

        logger.info("trace.span", extra={
            "trace_id": get_trace_id(),
            "span": span_name,
            "duration": round(duration, 4),
            "parent": parent,
        })

        _set_current_span(parent)


# ==========================================
# 🔥 DB TRACE WRAPPER
# ==========================================

def trace_db_query(execute, sql, params, many, context):
    from .metrics import (
        db_query_count_total,
        db_query_duration_seconds,
        db_slow_queries_total
    )

    start = time.time()

    try:
        return execute(sql, params, many, context)
    finally:
        duration = time.time() - start

        # 🔥 acumular stats en request
        _thread_locals.db_time += duration
        _thread_locals.db_queries += 1

        db_query_count_total.inc()
        db_query_duration_seconds.observe(duration)

        if duration > 0.1:
            _thread_locals.slow_queries += 1
            db_slow_queries_total.inc()

            import logging
            logger = logging.getLogger("inventory.domain")

            logger.warning("db.slow_query", extra={
                "trace_id": get_trace_id(),
                "duration": round(duration, 4),
                "sql": sql[:200],
            })