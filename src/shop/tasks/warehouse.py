"""src/shop/tasks/warehouse.py."""

import time

import redis
from celery import shared_task
from django.conf import settings

from src.shop.models import TaskRegistry

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@shared_task(name="shop.tasks.warehouse_audit")
def warehouse_audit_task():
    """Simulate a heavy mathematical operation for 5 seconds without sleep."""
    try:
        end_time = time.time() + 5.0
        counter = 0

        while time.time() < end_time:
            counter += 1
            _ = counter**2

        registry = TaskRegistry.objects.filter(task_name="warehouse_audit").first()
        if registry:
            registry.status = TaskRegistry.Status.COMPLETED
            registry.save()

    except Exception:
        registry = TaskRegistry.objects.filter(task_name="warehouse_audit").first()
        if registry:
            registry.status = TaskRegistry.Status.FAILED
            registry.save()
        raise

    else:
        return f"Аудит завершен. Итераций цикла: {counter}"

    finally:
        redis_client.delete("warehouse_audit_lock")
