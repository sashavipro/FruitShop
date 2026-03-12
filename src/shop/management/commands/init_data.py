"""src/shop/management/commands/init_data.py."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask

from src.shop.models import BankAccount
from src.shop.models import Product


class Command(BaseCommand):
    """Command to initialize the database with starting data."""

    help = (
        "Populates the database with initial "
        "fruits, bank balance, superuser, and periodic tasks."
    )

    def handle(self, *args, **kwargs):
        """Execute the command."""
        self.stdout.write("Начинаем инициализацию базы данных...")
        self._create_superuser()
        self._init_bank_account()
        self._init_products()
        self._init_periodic_tasks()
        self.stdout.write(
            self.style.SUCCESS("Инициализация базы данных полностью завершена!")
        )

    def _create_superuser(self):
        """Create a superuser if one does not already exist."""
        user_model = get_user_model()

        if not user_model.objects.filter(username="admin").exists():
            user_model.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(
                self.style.SUCCESS("Суперпользователь 'admin' (пароль: admin) создан.")
            )
        else:
            self.stdout.write(self.style.WARNING("Суперпользователь уже существует."))

    def _init_bank_account(self):
        """Initialize the company's bank account."""
        account, _ = BankAccount.objects.get_or_create(id=1)
        account.balance = 245.00
        account.save()
        self.stdout.write(self.style.SUCCESS("Баланс счета установлен на 245 USD."))

    def _init_products(self):
        """Fill the warehouse with initial fruit."""
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

    def _init_periodic_tasks(self):
        """Configure the schedule for Celery Beat in the database."""
        tasks_info = [
            ("buy-apples", "shop.tasks.trade_buy_apples", "*/1"),
            ("sell-apples", "shop.tasks.trade_sell_apples", "*/2"),
            ("buy-pineapples", "shop.tasks.trade_buy_pineapples", "*/2"),
            ("sell-pineapples", "shop.tasks.trade_sell_pineapples", "*/3"),
            ("buy-bananas", "shop.tasks.trade_buy_bananas", "*/3"),
            ("sell-bananas", "shop.tasks.trade_sell_bananas", "*/4"),
            ("buy-oranges", "shop.tasks.trade_buy_oranges", "*/4"),
            ("sell-oranges", "shop.tasks.trade_sell_oranges", "*/5"),
            ("buy-apricots", "shop.tasks.trade_buy_apricots", "*/2"),
            ("sell-apricots", "shop.tasks.trade_sell_apricots", "*/3"),
            ("buy-kiwi", "shop.tasks.trade_buy_kiwi", "*/3"),
            ("sell-kiwi", "shop.tasks.trade_sell_kiwi", "*/4"),
            ("buy-peaches", "shop.tasks.trade_buy_peaches", "*/4"),
            ("sell-peaches", "shop.tasks.trade_sell_peaches", "*/5"),
        ]

        for name, task_path, minute_cron in tasks_info:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute_cron,
                hour="*",
                day_of_week="*",
                day_of_month="*",
                month_of_year="*",
            )

            PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    "crontab": schedule,
                    "task": task_path,
                    "enabled": True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS("Все периодические задачи успешно загружены в БД!")  # noqa: RUF001
        )
