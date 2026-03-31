from django import forms
from .models import UserNotificationPreference
from notifications.preferences import EVENT_LABELS


class NotificationPreferencesForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not user:
            return

        prefs = {
            p.event_type: p
            for p in user.notification_preferences.all()
        }

        for event, label in EVENT_LABELS.items():
            pref = prefs.get(event)

            self.fields[event] = forms.BooleanField(
                label=label,
                required=False,
                initial=pref.enabled if pref else True,
            )