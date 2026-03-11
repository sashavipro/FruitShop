"""src/chat/consumers.py."""

import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string

from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer for handling real-time chat."""

    async def connect(self):
        """Accept connection and add to the chat room group."""
        self.room_group_name = "chat_room"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Remove from the group on disconnect."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive message from WebSocket, save to DB, and broadcast."""
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get("message")

        user = self.scope.get("user")

        if user and user.is_authenticated and message_text:
            msg = await self.save_message(user, message_text)

            html = await sync_to_async(render_to_string)(
                "includes/ws_chat_message.html", {"msg": msg}
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "html": html,
                },
            )

    async def chat_message(self, event):
        """Receive message from room group and send to WebSocket."""
        if "html" in event:
            await self.send(text_data=event["html"])
        else:
            await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, text):
        """Save a message to the database safely and synchronously."""
        return ChatMessage.objects.create(
            author_user=user, author_name=user.username, text=text
        )
