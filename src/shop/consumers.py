"""src/shop/consumers.py."""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TradeConsumer(AsyncWebsocketConsumer):
    """Consumer for broadcasting trade logs and balance updates."""

    async def connect(self):
        """Accept connection and add to the trade updates group."""
        self.group_name = "trade_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        user = self.scope.get("user")
        if user and user.is_authenticated:
            self.personal_group = f"user_{user.id}"
            await self.channel_layer.group_add(self.personal_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """Remove from the group on disconnect."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        if hasattr(self, "personal_group"):
            await self.channel_layer.group_discard(
                self.personal_group, self.channel_name
            )

    async def trade_update(self, event):
        """Receive a trade update from the group and send it to the client."""
        if "html" in event:
            await self.send(text_data=event["html"])
        else:
            await self.send(text_data=json.dumps(event))
