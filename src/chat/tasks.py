"""src/chat/tasks.py."""

import redis
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone

from .bot import get_joker_response
from .models import ChatMessage

# Подключаемся к Redis для проверки статуса
redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@shared_task(name="chat.tasks.joker_bot")
def joker_bot_task():
    """Recursive task to send a joke, broadcast it, and reschedule itself."""
    if redis_client.get("joker_active") != b"1":
        return "Бот отключен, рекурсия остановлена."

    last_user_msg = ChatMessage.objects.filter(author_user__isnull=False).first()
    prompt = (
        last_user_msg.text
        if last_user_msg
        else "Расскажи случайную шутку про склад фруктов."
    )

    joke_text = get_joker_response(prompt)

    msg = ChatMessage.objects.create(
        author_user=None, author_name="Шутник 🤡", text=joke_text
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_room",
        {
            "type": "chat_message",
            "message": msg.text,
            "author_name": msg.author_name,
            "created_at": timezone.localtime(msg.created_at).strftime("%H:%M"),
        },
    )

    delay = len(joke_text)
    delay = max(delay, 10)

    joker_bot_task.apply_async((), countdown=delay)

    return (
        f"Шутка на {len(joke_text)} символов отправлена. Следующая через {delay} сек."
    )
