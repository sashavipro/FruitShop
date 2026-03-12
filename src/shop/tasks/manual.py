"""src/shop/tasks/manual.py."""

from celery import shared_task

from .services import execute_trade


@shared_task(
    name="shop.tasks.trade_manual",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=5,
)
def trade_manual(action: str, product_name: str, quantity: int):
    """Execute a manual trade initiated from the frontend API."""
    execute_trade(action, product_name, quantity)
