"""src/shop/tasks/warehouse.py."""

import time

import redis
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings

from src.shop.models import TaskRegistry

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@shared_task(name="shop.tasks.warehouse_audit")
def warehouse_audit_task():
    """Simulate a long audit operation (15 seconds) and send progress to WS."""
    channel_layer = get_channel_layer()
    total_steps = 15

    try:
        for step in range(1, total_steps + 1):
            time.sleep(1)
            progress = int((step / total_steps) * 100)

            async_to_sync(channel_layer.group_send)(
                "trade_updates",
                {
                    "type": "trade_update",
                    "event_type": "audit_progress",
                    "progress": progress,
                },
            )

        registry = TaskRegistry.objects.filter(task_name="warehouse_audit").first()
        if registry:
            registry.status = TaskRegistry.Status.COMPLETED
            registry.save()

        async_to_sync(channel_layer.group_send)(
            "trade_updates",
            {
                "type": "trade_update",
                "event_type": "audit_complete",
            },
        )

    except Exception:
        registry = TaskRegistry.objects.filter(task_name="warehouse_audit").first()
        if registry:
            registry.status = TaskRegistry.Status.FAILED
            registry.save()

        async_to_sync(channel_layer.group_send)(
            "trade_updates",
            {
                "type": "trade_update",
                "event_type": "audit_failed",
            },
        )
        raise

    finally:
        redis_client.delete("warehouse_audit_lock")

    return "Аудит завершен на 100%"
