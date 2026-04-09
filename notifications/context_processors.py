from notifications.models import UserNotification


def notifications_unread(request):
    if not request.user.is_authenticated:
        return {"notifications_unread": 0}

    count = UserNotification.objects.filter(
        user=request.user,
        seen=False,
        notification__organization=request.organization
    ).count()

    return {"notifications_unread": count}