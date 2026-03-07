"""src/core/routing.py."""

from django.urls import path

from src.chat.consumers import ChatConsumer
from src.shop.consumers import TradeConsumer

websocket_urlpatterns = [
    path("ws/trades/", TradeConsumer.as_asgi()),
    path("ws/chat/", ChatConsumer.as_asgi()),
]
