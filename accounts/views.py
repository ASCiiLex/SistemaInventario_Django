from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import NotificationPreferencesForm
from .models import UserNotificationPreference
from notifications.preferences import ensure_user_preferences, EVENT_LABELS


@login_required
def notification_preferences(request):
    user = request.user

    ensure_user_preferences(user)

    if request.method == "POST":
        form = NotificationPreferencesForm(request.POST, user=user)

        if form.is_valid():
            for event in EVENT_LABELS.keys():
                enabled = form.cleaned_data.get(event, False)

                UserNotificationPreference.objects.update_or_create(
                    user=user,
                    event_type=event,
                    defaults={"enabled": enabled},
                )

            # limpiar cache
            if hasattr(user, "_pref_cache"):
                del user._pref_cache

            return redirect("notification_preferences")

    else:
        form = NotificationPreferencesForm(user=user)

    return render(request, "accounts/notification_preferences.html", {
        "form": form
    })