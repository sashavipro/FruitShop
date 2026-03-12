"""src/shop/tasks/peaches.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(
    name="shop.tasks.trade_buy_peaches",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=5,
)
def trade_buy_peaches():
    """Execute a buy trade for a random quantity of peaches."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Персики", quantity)


@shared_task(
    name="shop.tasks.trade_sell_peaches",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=5,
)
def trade_sell_peaches():
    """Execute a sell trade for a random quantity of peaches."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Персики", quantity)
