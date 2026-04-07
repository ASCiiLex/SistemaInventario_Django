import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.user_group = f"user_{user.id}"
        self.global_group = "notifications_global"

        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.global_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

        if hasattr(self, "global_group"):
            await self.channel_layer.group_discard(
                self.global_group,
                self.channel_name
            )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        await self.send(
            text_data=json.dumps({
                "event": event["data"].get("event"),
                "type": event["data"].get("type"),  # compatibilidad
                "message": event["data"].get("message"),
                "product": event["data"].get("product"),
            })
        )