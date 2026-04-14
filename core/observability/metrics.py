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
    ["method", "endpoint"]
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