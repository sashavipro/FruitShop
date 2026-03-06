"""src/shop/tasks/bananas.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(name="shop.tasks.trade_buy_bananas")
def trade_buy_bananas():
    """Execute a buy trade for a random quantity of bananas."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Бананы", quantity)


@shared_task(name="shop.tasks.trade_sell_bananas")
def trade_sell_bananas():
    """Execute a sell trade for a random quantity of bananas."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Бананы", quantity)
