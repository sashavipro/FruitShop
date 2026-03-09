"""src/chat/bot.py."""

import logging
import secrets

from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

FALLBACK_JOKES = [
    "Почему бухгалтер не ест бананы? Потому что они не сходятся по балансу! 🍌",
    "На складе недостача: пропала тонна яблок. "  # noqa: RUF001
    "Видимо, Ньютон переборщил с экспериментами. 🍏",  # noqa: RUF001
    "Какой самый страшный сон кладовщика? Бесконечная инвентаризация ананасов! 🍍",
    "Если сложить все наши персики в одну линию... "
    "то продажи всё равно не вырастут. 🍑",
    "Я искусственный интеллект, а вы всё ещё считаете "  # noqa: RUF001
    "остатки в Excel. Кто тут еще робот? 🤖",
    "Аудит прошел успешно! Мы нашли 3 лишних киви и потеряли совесть. 🥝",
]


def get_joker_response(user_text: str) -> str:
    """Fetch a funny response from Gemini API based on user input."""
    if (
        not settings.GEMINI_API_KEY
        or settings.GEMINI_API_KEY == "твой_секретный_ключ_gemini_здесь"
    ):
        return secrets.choice(FALLBACK_JOKES)

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Ты бот-Шутник в корпоративном чате магазина фруктов. "
                    "Твоя задача - отвечать на сообщения пользователей короткими, "
                    "смешными шутками, сарказмом или каламбурами про фрукты, "
                    "бухгалтерию, склад и торговлю. Отвечай кратко, "
                    "максимум 1-2 предложения."
                )
            ),
        )
        return response.text.strip()

    except Exception:
        logger.exception("Ошибка Gemini API")
        return secrets.choice(FALLBACK_JOKES)
