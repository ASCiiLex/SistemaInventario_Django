from .metrics import domain_events_total


def track_event(event_type: str):
    domain_events_total.labels(event_type=event_type).inc()