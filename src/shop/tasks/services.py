"""src/shop/tasks/services.py."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone

from src.shop.models import BankAccount
from src.shop.models import Product
from src.shop.models import TradeLog


def broadcast_update(log_entry, account, product):
    """Send updated data to the WebSocket group."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "trade_updates",
        {
            "type": "trade_update",
            "log": {
                "status": log_entry.status,
                "message": log_entry.message,
                "created_at": timezone.localtime(log_entry.created_at).strftime(
                    "%d.%m.%Y %H:%M"
                ),
            },
            "balance": str(account.balance),
            "product": {
                "name": product.name,
                "quantity": product.stock_quantity,
                "last_operation": product.last_operation_info,
            },
        },
    )


def execute_trade(action: str, product_name: str, quantity: int) -> None:
    """Execute buy or sell operation atomically."""
    with transaction.atomic():
        # Блокируем строки в БД до завершения транзакции
        account = BankAccount.objects.select_for_update().first()
        try:
            product = Product.objects.select_for_update().get(name=product_name)
        except Product.DoesNotExist:
            return

        current_time = timezone.localtime().strftime("%d.%m.%Y %H:%M")

        if action == "buy":
            cost = product.buy_price * quantity
            if account.balance >= cost:
                account.balance -= cost
                product.stock_quantity += quantity

                account.save()

                operation_msg = (
                    f"куплено {quantity} {product_name.lower()} за {cost} usd"
                )
                product.last_operation_info = f"{current_time} - {operation_msg}"
                product.save()

                log_msg = (
                    f"Поставщик привёз {quantity} {product_name.lower()}."
                    f" Со счёта списано {cost} USD, покупка завершена."  # noqa: RUF001
                )
                log_entry = TradeLog.objects.create(
                    status=TradeLog.Status.SUCCESS, message=log_msg
                )
                broadcast_update(log_entry, account, product)
            else:
                log_msg = (
                    f"Поставщик привёз {quantity} {product_name.lower()}."
                    f" Недостаточно средств на счету, закупка отменена."
                )
                log_entry = TradeLog.objects.create(
                    status=TradeLog.Status.ERROR, message=log_msg
                )
                broadcast_update(log_entry, account, product)

        elif action == "sell":
            revenue = product.sell_price * quantity
            if product.stock_quantity >= quantity:
                account.balance += revenue
                product.stock_quantity -= quantity

                account.save()

                operation_msg = (
                    f"продано {quantity} {product_name.lower()} за {revenue} usd"
                )
                product.last_operation_info = f"{current_time} - {operation_msg}"
                product.save()

                log_msg = (
                    f"Покупатель купил {quantity} {product_name.lower()}."
                    f" На счёт зачислено {revenue} USD, продажа завершена."  # noqa: RUF001
                )
                log_entry = TradeLog.objects.create(
                    status=TradeLog.Status.SUCCESS, message=log_msg
                )
                broadcast_update(log_entry, account, product)
            else:
                log_msg = (
                    f"Покупатель запросил {quantity} {product_name.lower()}."
                    f" Недостаточно товара на складе, продажа отменена."
                )
                log_entry = TradeLog.objects.create(
                    status=TradeLog.Status.ERROR, message=log_msg
                )
                broadcast_update(log_entry, account, product)
