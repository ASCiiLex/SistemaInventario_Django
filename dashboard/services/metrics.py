from django.core.cache import cache
from prometheus_client import REGISTRY
import logging

metrics_logger = logging.getLogger("inventory.metrics")


def _get_prometheus_metric_value(metric_name):
    for metric in REGISTRY.collect():
        if metric.name == metric_name:
            total = 0
            for sample in metric.samples:
                if sample.name.endswith("_total") or sample.name == metric_name:
                    total += sample.value
            return total
    return 0


def get_system_metrics(organization):
    cache_key = f"dashboard:system_metrics:{organization.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    total_requests = _get_prometheus_metric_value("http_requests")
    total_errors = _get_prometheus_metric_value("errors")
    total_events = _get_prometheus_metric_value("domain_events")

    result = {
        "requests": int(total_requests),
        "errors": int(total_errors),
        "events": int(total_events),
    }

    cache.set(cache_key, result, 5)

    metrics_logger.info("dashboard.system_metrics.prometheus", extra={
        "org_id": organization.id,
        **result
    })

    return result