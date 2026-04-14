from django.core.cache import cache
from prometheus_client import REGISTRY
import logging

metrics_logger = logging.getLogger("inventory.metrics")


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


def get_system_metrics(organization):
    cache_key = f"dashboard:system_metrics:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    requests_samples = _collect_metric("http_requests")
    errors_samples = _collect_metric("errors")
    events_samples = _collect_metric("domain_events")

    total_requests = int(_sum_samples(requests_samples))
    total_errors = int(_sum_samples(errors_samples))
    total_events = int(_sum_samples(events_samples))

    avg_latency = _get_histogram_avg("http_request_duration_seconds")

    result = {
        "requests": total_requests,
        "errors": total_errors,
        "events": total_events,
        "avg_latency": avg_latency,
    }

    cache.set(cache_key, result, 5)

    metrics_logger.info("dashboard.system_metrics.prometheus", extra={
        "org_id": organization.id,
        **result
    })

    return result