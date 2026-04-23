from django.core.cache import cache
from prometheus_client import REGISTRY
import logging
import time

metrics_logger = logging.getLogger("inventory.metrics")


def _safe_cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def _safe_cache_set(key, value, ttl):
    try:
        cache.set(key, value, ttl)
    except Exception:
        pass


def _collect_metric(metric_name):
    for metric in REGISTRY.collect():
        if metric.name == metric_name:
            return metric.samples
    return []


def _sum_samples(samples):
    return sum(sample.value for sample in samples)


def _get_histogram_avg(metric_name):
    samples = _collect_metric(metric_name)

    sum_value = 0
    count_value = 0

    for s in samples:
        if s.name.endswith("_sum"):
            sum_value += s.value
        elif s.name.endswith("_count"):
            count_value += s.value

    if count_value == 0:
        return 0

    return round(sum_value / count_value, 4)


def _get_histogram_p95(metric_name):
    samples = _collect_metric(metric_name)

    buckets = {}

    for s in samples:
        if "_bucket" in s.name:
            le = float(s.labels.get("le", 0))
            buckets[le] = buckets.get(le, 0) + s.value

    if not buckets:
        return 0

    sorted_buckets = sorted(buckets.items())
    total = sorted_buckets[-1][1]

    if total == 0:
        return 0

    target = total * 0.95

    for le, value in sorted_buckets:
        if value >= target:
            return le

    return sorted_buckets[-1][0]


def _get_top_endpoints():
    samples = _collect_metric("http_request_duration_seconds")

    endpoint_times = {}
    endpoint_counts = {}

    for s in samples:
        if s.name.endswith("_sum"):
            endpoint = s.labels.get("endpoint", "unknown")
            endpoint_times[endpoint] = endpoint_times.get(endpoint, 0) + s.value

        elif s.name.endswith("_count"):
            endpoint = s.labels.get("endpoint", "unknown")
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + s.value

    results = []

    for endpoint in endpoint_times:
        count = endpoint_counts.get(endpoint, 1)
        avg = endpoint_times[endpoint] / count if count else 0

        results.append({
            "endpoint": endpoint,
            "avg_latency": round(avg, 4),
            "hits": int(count),
        })

    results.sort(key=lambda x: x["avg_latency"], reverse=True)

    return results[:5]


def _calculate_rate(metric_name, cache_key):
    current = int(_sum_samples(_collect_metric(metric_name)))
    now = time.time()

    prev = _safe_cache_get(cache_key)

    if not prev:
        _safe_cache_set(cache_key, {"value": current, "ts": now}, 60)
        return 0

    delta_value = current - prev["value"]
    delta_time = now - prev["ts"]

    rate = (delta_value / delta_time) if delta_time > 0 else 0

    _safe_cache_set(cache_key, {"value": current, "ts": now}, 60)

    return round(rate, 2)


def _evaluate_alerts(metrics):
    alerts = []

    if metrics["errors"] > 10:
        alerts.append({"level": "critical", "msg": "Demasiados errores"})

    if metrics["p95_latency"] > 1:
        alerts.append({"level": "warning", "msg": "Latencia elevada"})

    if metrics["requests"] == 0:
        alerts.append({"level": "warning", "msg": "Sin tráfico detectado"})

    if metrics["rps"] > 50:
        alerts.append({"level": "warning", "msg": "Alta carga de tráfico"})

    return alerts


def _calculate_health_score(metrics):
    score = 100

    if metrics["errors"] > 10:
        score -= 40
    elif metrics["errors"] > 0:
        score -= 20

    if metrics["p95_latency"] > 1:
        score -= 30
    elif metrics["p95_latency"] > 0.5:
        score -= 10

    if metrics["requests"] == 0:
        score -= 30

    if metrics["rps"] > 50:
        score -= 10

    return max(score, 0)


def get_system_metrics(organization):
    cache_key = f"dashboard:system_metrics:{organization.id}"
    cached = _safe_cache_get(cache_key)
    if cached:
        return cached

    requests_samples = _collect_metric("http_requests")
    errors_samples = _collect_metric("errors")
    events_samples = _collect_metric("domain_events")

    total_requests = int(_sum_samples(requests_samples))
    total_errors = int(_sum_samples(errors_samples))
    total_events = int(_sum_samples(events_samples))

    avg_latency = _get_histogram_avg("http_request_duration_seconds")
    p95_latency = _get_histogram_p95("http_request_duration_seconds")

    top_endpoints = _get_top_endpoints()

    rps = _calculate_rate("http_requests", "metrics:rps")
    eps = _calculate_rate("errors", "metrics:eps")
    evps = _calculate_rate("domain_events", "metrics:evps")

    base_metrics = {
        "requests": total_requests,
        "errors": total_errors,
        "events": total_events,
        "avg_latency": avg_latency,
        "p95_latency": p95_latency,
        "top_endpoints": top_endpoints,
        "rps": rps,
        "eps": eps,
        "evps": evps,
    }

    alerts = _evaluate_alerts(base_metrics)
    health_score = _calculate_health_score(base_metrics)

    result = {
        **base_metrics,
        "alerts": alerts,
        "health_score": health_score,
    }

    _safe_cache_set(cache_key, result, 5)

    metrics_logger.info("dashboard.system_metrics.prometheus", extra={
        "org_id": organization.id,
        **result
    })

    return result