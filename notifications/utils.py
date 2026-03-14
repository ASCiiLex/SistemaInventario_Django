from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def broadcast_notification(data: dict):
    layer = get_channel_layer()
    if not layer:
        return
    async_to_sync(layer.group_send)(
        "notifications_global",
        {
            "type": "send_notification",
            "data": data
        }
    )