from .models import Notification


def notifications_unread(request):
    return {
        "notifications_unread": Notification.objects.filter(seen=False).count()
    }