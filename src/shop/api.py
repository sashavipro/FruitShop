"""src/shop/api.py."""

from pathlib import Path

import redis
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from ninja import File
from ninja import Form
from ninja import NinjaAPI
from ninja.files import UploadedFile
from ninja.security import django_auth

from src.chat.api import router as chat_router

from .models import Declaration
from .models import TaskRegistry
from .tasks.manual import trade_manual
from .tasks.warehouse import warehouse_audit_task

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
