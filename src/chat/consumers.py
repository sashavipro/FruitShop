"""src/chat/consumers.py."""

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

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

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": msg.text,
                    "author_name": msg.author_name,
                    "created_at": msg.created_at.strftime("%H:%M"),
                },
            )

    async def chat_message(self, event):
        """Receive message from room group and send to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "message": event["message"],
                    "author_name": event["author_name"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, user, text):
        """Save a message to the database safely and synchronously."""
        return ChatMessage.objects.create(
            author_user=user, author_name=user.username, text=text
        )
