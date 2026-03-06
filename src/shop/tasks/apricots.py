"""src/shop/tasks/apricots.py."""

import random

from celery import shared_task

from .services import execute_trade


@shared_task(name="shop.tasks.trade_buy_apricots")
def trade_buy_apricots():
    """Execute a buy trade for a random quantity of apricots."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("buy", "Абрикосы", quantity)


@shared_task(name="shop.tasks.trade_sell_apricots")
def trade_sell_apricots():
    """Execute a sell trade for a random quantity of apricots."""
    quantity = random.randint(1, 10)  # noqa: S311
    execute_trade("sell", "Абрикосы", quantity)
