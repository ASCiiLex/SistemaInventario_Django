from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_to_user(user_id: int, data: dict):
    layer = get_channel_layer()
    if not layer:
        return

    async_to_sync(layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "data": data,
        },
    )


def send_ui_event_to_all(data: dict):
    layer = get_channel_layer()
    if not layer:
        return

    async_to_sync(layer.group_send)(
        "notifications_global",
        {
            "type": "send_notification",
            "data": {
                "event": data.get("event", "ui"),
                "type": data.get("type", "notification"),
                "message": data.get("message"),
                "product": data.get("product"),
            },
        },
    )