"""src/shop/tasks/kiwi.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(name="shop.tasks.trade_buy_kiwi")
def trade_buy_kiwi():
    """Execute a buy trade for a random quantity of kiwi."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Киви", quantity)


@shared_task(name="shop.tasks.trade_sell_kiwi")
def trade_sell_kiwi():
    """Execute a sell trade for a random quantity of kiwi."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Киви", quantity)
