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
    UserNotificationPreference = _get_model()

    pref = (
        UserNotificationPreference.objects
        .filter(user=user, event_type=event_type)
        .first()
    )

    if not pref:
        return True

    return pref.enabled