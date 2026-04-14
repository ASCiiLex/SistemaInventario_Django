from .metrics import errors_total


def track_error(error_type: str):
    errors_total.labels(type=error_type).inc()