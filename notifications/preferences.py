from django.contrib.auth.models import User
from django.apps import apps


DEFAULT_EVENTS = [
    "stock_item_low",
    "product_risk",
    "order_created",
]


def _get_model():
    return apps.get_model("notifications", "UserNotificationPreference")


def ensure_user_preferences(user: User):
    UserNotificationPreference = _get_model()

    existing = set(
        UserNotificationPreference.objects.filter(user=user)
        .values_list("event_type", flat=True)
    )

    to_create = [
        UserNotificationPreference(user=user, event_type=event)
        for event in DEFAULT_EVENTS
        if event not in existing
    ]

    if to_create:
        UserNotificationPreference.objects.bulk_create(to_create)


def is_event_enabled(user: User, event_type: str) -> bool:
    prefs = getattr(user, "_pref_cache", None)

    if prefs is None:
        prefs = {
            p.event_type: p.enabled
            for p in user.notification_preferences.all()
        }
        user._pref_cache = prefs

    return prefs.get(event_type, True)