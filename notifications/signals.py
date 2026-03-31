from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Notification, UserNotification
from .preferences import is_event_enabled


@receiver(post_save, sender=Notification)
def create_user_notifications(sender, instance, created, **kwargs):
    if not created:
        return

    users = User.objects.prefetch_related("notification_preferences")

    bulk = []

    for user in users:
        if not is_event_enabled(user, instance.type):
            continue

        bulk.append(
            UserNotification(
                user=user,
                notification=instance,
            )
        )

    if bulk:
        UserNotification.objects.bulk_create(bulk)