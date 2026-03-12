"""src/shop/tasks/oranges.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(
    name="shop.tasks.trade_buy_oranges",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=5,
)
def trade_buy_oranges():
    """Execute a buy trade for a random quantity of oranges."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Апельсины", quantity)


@shared_task(
    name="shop.tasks.trade_sell_oranges",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=5,
)
def trade_sell_oranges():
    """Execute a sell trade for a random quantity of oranges."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Апельсины", quantity)
