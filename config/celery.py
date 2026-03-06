"""config/celery.py."""

import os

from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("fruitshop")

# Используем строку 'django.conf:settings', чтобы рабочий процесс не сериализовал объект настроек.
# Пространство имен 'CELERY' означает, что все ключи конфигурации Celery в settings.py
# должны начинаться с 'CELERY_'
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
