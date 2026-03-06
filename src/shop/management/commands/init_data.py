"""src/shop/management/commands/init_data.py."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from src.shop.models import BankAccount
from src.shop.models import Product


class Command(BaseCommand):
    """Command to initialize the database with starting data."""

    help = "Populates the database with initial fruits, bank balance, and superuser."

    def handle(self, *args, **kwargs):
        """Execute the command."""
        user_model = get_user_model()

        if not user_model.objects.filter(username="admin").exists():
            user_model.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(
                self.style.SUCCESS("Суперпользователь 'admin' (пароль: admin) создан.")
            )
        else:
            self.stdout.write(self.style.WARNING("Суперпользователь уже существует."))

        account, _ = BankAccount.objects.get_or_create(id=1)
        account.balance = 245.00
        account.save()
        self.stdout.write(self.style.SUCCESS("Баланс счета установлен на 245 USD."))

        fruits_data = [
            {
                "name": "Ананасы",
                "stock_quantity": 15,
                "buy_price": 3.00,
                "sell_price": 4.00,
            },
            {
                "name": "Яблоки",
                "stock_quantity": 224,
                "buy_price": 4.00,
                "sell_price": 5.00,
            },
            {
                "name": "Бананы",
                "stock_quantity": 66,
                "buy_price": 1.00,
                "sell_price": 2.00,
            },
            {
                "name": "Апельсины",
                "stock_quantity": 235,
                "buy_price": 2.00,
                "sell_price": 3.00,
            },
            {
                "name": "Абрикосы",
                "stock_quantity": 12,
                "buy_price": 3.00,
                "sell_price": 5.00,
            },
            {
                "name": "Киви",
                "stock_quantity": 0,
                "buy_price": 4.00,
                "sell_price": 6.00,
            },
            {
                "name": "Персики",
                "stock_quantity": 0,
                "buy_price": 2.00,
                "sell_price": 3.00,
            },
        ]

        for item in fruits_data:
            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults=item,
            )
            if not created:
                for key, value in item.items():
                    setattr(product, key, value)
                product.save()

        self.stdout.write(self.style.SUCCESS("Товары на складе успешно обновлены."))
