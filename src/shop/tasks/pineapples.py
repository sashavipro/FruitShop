"""src/shop/tasks/pineapples.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(name="shop.tasks.trade_buy_pineapples")
def trade_buy_pineapples():
    """Execute a buy trade for a random quantity of pineapples."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Ананасы", quantity)


@shared_task(name="shop.tasks.trade_sell_pineapples")
def trade_sell_pineapples():
    """Execute a sell trade for a random quantity of pineapples."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Ананасы", quantity)
