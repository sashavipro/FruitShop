"""src/shop/api.py."""

from decimal import Decimal
from pathlib import Path

import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from ninja import File
from ninja import Form
from ninja import NinjaAPI
from ninja.files import UploadedFile
from ninja.security import django_auth

from src.chat.api import router as chat_router

from .models import BankAccount
from .models import Declaration
from .models import TaskRegistry
from .models import TradeLog
from .tasks.manual import trade_manual
from .tasks.warehouse import warehouse_audit_task
from .tasks.warehouse import warehouse_check_task

api = NinjaAPI(auth=django_auth)
api.add_router("", chat_router)
redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@api.post("/trade/")
def create_trade_task(
    request: HttpRequest,
    action: str = Form(...),
    product_name: str = Form(...),
    quantity: int = Form(...),
):
    """Put a manual trade task into the Celery queue."""
    if quantity <= 0:
        return {
            "status": "error",
            "message": "Ошибка: количество товара должно быть больше нуля!",
        }

    trade_manual.delay(action, product_name, quantity)

    return {
        "status": "ok",
        "message": f"Задача на {action} {quantity} {product_name} в очереди",
    }


@api.post("/audit/")
def start_audit(request: HttpRequest):
    """Start the warehouse audit task with Redis lock protection."""
    if redis_client.get("warehouse_audit_lock"):
        return {
            "status": "error",
            "message": "Аудит уже выполняется. Дождитесь завершения!",
        }

    redis_client.set("warehouse_audit_lock", "locked", ex=30)

    registry, _ = TaskRegistry.objects.get_or_create(task_name="warehouse_audit")
    registry.status = TaskRegistry.Status.RUNNING
    registry.save()

    warehouse_audit_task.delay()

    return {"status": "ok", "message": "Аудит успешно запущен"}


@api.post("/check-warehouse/")
def start_warehouse_check(request: HttpRequest):
    """Start warehouse check with material cycle (Redis Lock protection)."""
    user = request.user
    if not user.is_authenticated:
        return {"status": "error", "message": "Необходима авторизация"}

    if redis_client.get("warehouse_check_lock"):
        return {
            "status": "error",
            "message": "Проверка склада уже выполняется! Дождитесь завершения.",
        }

    redis_client.set("warehouse_check_lock", "locked", ex=10)

    registry, _ = TaskRegistry.objects.get_or_create(task_name="warehouse_check")
    registry.status = TaskRegistry.Status.RUNNING
    registry.save()

    warehouse_check_task.delay(user.id)

    return {"status": "ok", "message": "Математическая проверка склада запущена!"}


@api.get("/audit/status/")
def get_audit_status(request: HttpRequest):
    """Get the current status of the audit task for frontend polling."""
    registry = TaskRegistry.objects.filter(task_name="warehouse_audit").first()
    status = registry.status if registry else TaskRegistry.Status.IDLE
    return {"status": status}


@api.get("/tasks/")
def get_all_tasks(request: HttpRequest):
    """Return a JSON with the latest run dates of all registered tasks."""
    tasks = TaskRegistry.objects.all()

    result = [
        {
            "task_name": task.task_name,
            "status": task.status,
            "last_run_at": timezone.localtime(task.last_run_at).strftime(
                "%d.%m.%Y %H:%M:%S"
            ),
        }
        for task in tasks
    ]

    return {"tasks": result}


@api.post("/upload-declaration/")
def upload_declaration(request, file: UploadedFile = File(...)):  # noqa: B008
    """Upload and validate declaration files (multipart/form-data)."""
    allowed_extensions = [".pdf", ".csv", ".xlsx", ".xls"]
    ext = Path(file.name).suffix.lower()

    if ext not in allowed_extensions:
        allowed = ", ".join(allowed_extensions)
        return {
            "status": "error",
            "message": f"Неверный формат: {ext}. Разрешены: {allowed}",
        }

    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        return {
            "status": "error",
            "message": "Файл слишком большой! Максимальный размер: 5 МБ.",
        }

    declaration = Declaration()
    declaration.file.save(file.name, file)
    declaration.save()

    total_count = Declaration.objects.count()

    return {
        "status": "ok",
        "message": f"Декларация '{file.name}' успешно загружена!",
        "total_count": total_count,
    }


@api.post("/balance/")
def update_balance(
    request: HttpRequest,
    action: str = Form(...),
    amount: Decimal = Form(...),  # noqa: B008
):
    """Deposit or withdraw money from the bank account."""
    if amount <= 0:
        return {"status": "error", "message": "Сумма должна быть больше нуля!"}

    with transaction.atomic():
        account = BankAccount.objects.select_for_update().first()
        if not account:
            return {"status": "error", "message": "Счет не найден."}

        if action == "deposit":
            account.balance += amount
            msg = f"Счет пополнен на {amount} USD."
            status = TradeLog.Status.SUCCESS

        elif action == "withdraw":
            if account.balance >= amount:
                account.balance -= amount
                msg = f"Со счета выведено {amount} USD."  # noqa: RUF001
                status = TradeLog.Status.SUCCESS
            else:
                msg = f"Ошибка вывода: недостаточно средств ({amount} USD)."
                status = TradeLog.Status.ERROR
        else:
            return {"status": "error", "message": "Неизвестное действие."}

        if status == TradeLog.Status.SUCCESS:
            account.save()

        log_entry = TradeLog.objects.create(status=status, message=msg)

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
            },
        )

    if status == TradeLog.Status.ERROR:
        return {"status": "error", "message": msg}

    return {"status": "ok", "message": msg}
