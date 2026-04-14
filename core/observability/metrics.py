from prometheus_client import Counter, Histogram

# ==========================================
# HTTP METRICS
# ==========================================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(
        0.005, 0.01, 0.025, 0.05,
        0.1, 0.25, 0.5,
        1, 2.5, 5, 10
    )
)

# ==========================================
# ERRORS
# ==========================================

errors_total = Counter(
    "errors_total",
    "Total errors captured",
    ["type"]
)

# ==========================================
# DOMAIN EVENTS
# ==========================================

domain_events_total = Counter(
    "domain_events_total",
    "Total domain events emitted",
    ["event_type"]
)

# ==========================================
# 🔥 DB METRICS
# ==========================================

db_query_count_total = Counter(
    "db_query_count_total",
    "Total number of DB queries"
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "DB query duration in seconds",
    buckets=(
        0.001, 0.005, 0.01, 0.025,
        0.05, 0.1, 0.25, 0.5,
        1, 2.5, 5
    )
)

db_slow_queries_total = Counter(
    "db_slow_queries_total",
    "Total slow DB queries"
)