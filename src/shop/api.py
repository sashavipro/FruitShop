"""src/shop/api.py."""

from django.http import HttpRequest
from ninja import Form
from ninja import NinjaAPI

from src.shop.tasks.manual import trade_manual

api = NinjaAPI()


@api.post("/trade/")
def create_trade_task(
    request: HttpRequest,
    action: str = Form(...),
    product_name: str = Form(...),
    quantity: int = Form(...),
):
    """Put a manual trade task into the Celery queue."""
    trade_manual.delay(action, product_name, quantity)

    return {
        "status": "ok",
        "message": f"Задача на {action} {quantity} {product_name} в очереди",
    }
