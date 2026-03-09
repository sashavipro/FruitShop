#!/bin/bash
set -e

echo "==> Применение миграций базы данных..."
poetry run python manage.py migrate

echo "==> Инициализация базовых данных (init_data)..."
poetry run python manage.py init_data

echo "==> Запуск основного процесса..."
exec "$@"
