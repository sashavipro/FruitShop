"""src/shop/tasks/services.py."""

from django.db import transaction

from src.shop.models import BankAccount
from src.shop.models import Product
from src.shop.models import TradeLog


def execute_trade(action: str, product_name: str, quantity: int) -> None:
    """Execute buy or sell operation atomically."""
    with transaction.atomic():
        # Блокируем строки в БД до завершения транзакции
        account = BankAccount.objects.select_for_update().first()
        try:
            product = Product.objects.select_for_update().get(name=product_name)
        except Product.DoesNotExist:
            return

        if action == "buy":
            cost = product.buy_price * quantity
            if account.balance >= cost:
                account.balance -= cost
                product.stock_quantity += quantity

                account.save()

                operation_msg = (
                    f"куплено {quantity} {product_name.lower()} за {cost} usd"
                )
                product.last_operation_info = f"Сегодня - {operation_msg}"
                product.save()

                log_msg = (
                    f"Поставщик привёз {quantity} {product_name.lower()}."
                    f" Со счёта списано {cost} USD, покупка завершена."  # noqa: RUF001
                )
                TradeLog.objects.create(status=TradeLog.Status.SUCCESS, message=log_msg)
            else:
                log_msg = (
                    f"Поставщик привёз {quantity} {product_name.lower()}."
                    f" Недостаточно средств на счету, закупка отменена."
                )
                TradeLog.objects.create(status=TradeLog.Status.ERROR, message=log_msg)

        elif action == "sell":
            revenue = product.sell_price * quantity
            if product.stock_quantity >= quantity:
                account.balance += revenue
                product.stock_quantity -= quantity

                account.save()

                operation_msg = (
                    f"продано {quantity} {product_name.lower()} за {revenue} usd"
                )
                product.last_operation_info = f"Сегодня - {operation_msg}"
                product.save()

                log_msg = (
                    f"Покупатель купил {quantity} {product_name.lower()}."
                    f" На счёт зачислено {revenue} USD, продажа завершена."  # noqa: RUF001
                )
                TradeLog.objects.create(status=TradeLog.Status.SUCCESS, message=log_msg)
            else:
                log_msg = (
                    f"Покупатель запросил {quantity} {product_name.lower()}."
                    f" Недостаточно товара на складе, продажа отменена."
                )
                TradeLog.objects.create(status=TradeLog.Status.ERROR, message=log_msg)
