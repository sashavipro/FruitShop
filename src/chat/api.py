"""src/chat/api.py."""

import redis
from django.conf import settings
from django.http import HttpRequest
from ninja import Router

from .tasks import joker_bot_task

router = Router()
redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@router.post("/wake-joker/")
def wake_joker(request: HttpRequest):
    """Manually wake up the Joker bot from the frontend."""
    if redis_client.get("joker_active") == b"1":
        return {"status": "info", "message": "Шутник уже работает!"}

    redis_client.set("joker_active", "1")
    joker_bot_task.delay()
    return {"status": "ok", "message": "Бот Шутник успешно запущен!"}


@router.post("/sleep-joker/")
def sleep_joker(request: HttpRequest):
    """Stop the Joker bot."""
    redis_client.set("joker_active", "0")
    return {"status": "ok", "message": "Бот ушел в спячку 😴"}


@router.get("/joker-status/")
def joker_status(request: HttpRequest):
    """Check if the Joker bot is currently active."""
    is_active = redis_client.get("joker_active") == b"1"
    return {"is_active": is_active}
