"""src/shop/tasks/apples.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(name="shop.tasks.trade_buy_apples")
def trade_buy_apples():
    """Execute a buy trade for a random quantity of apples."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Яблоки", quantity)


@shared_task(name="shop.tasks.trade_sell_apples")
def trade_sell_apples():
    """Execute a sell trade for a random quantity of apples."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Яблоки", quantity)
