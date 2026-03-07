.PHONY: help run makemigrations migrate shell superuser init-data lint format up down test

# ==========================================
# Help
# ==========================================

# Вывод списка всех доступных команд
help:
	@echo "Доступные команды:"
	@echo "  make help           - Показать это сообщение"
	@echo "  make run            - Запуск сервера разработки"
	@echo "  make makemigrations - Создание новых миграций"
	@echo "  make migrate        - Применение миграций к БД"
	@echo "  make shell          - Запуск интерактивной консоли"
	@echo "  make superuser      - Стандартное создание суперпользователя"
	@echo "  make init-data      - Наша кастомная команда для наполнения БД"
	@echo "  make lint           - Проверка кода линтером Ruff"
	@echo "  make format         - Автоматическое форматирование кода (Ruff)"
	@echo "  make up             - Запуск БД и Redis в фоновом режиме"
	@echo "  make down           - Остановка контейнеров"
	@echo "  make test           - Запуск тестов"
	@echo "  make celery-trade   - Запуск Celery воркера для торговых операций (Очередь 1)"
	@echo "  make celery-warehouse - Запуск Celery воркера для складских операций (Очередь 2)"
	@echo "  make celery-beat    - Запуск планировщика периодических задач Celery Beat"

# ==========================================
# Django Commands
# ==========================================

# Запуск сервера разработки
run:
	poetry run python manage.py runserver

# Создание новых миграций
makemigrations:
	poetry run python manage.py makemigrations

# Применение миграций к БД
migrate:
	poetry run python manage.py migrate

# Запуск интерактивной консоли
shell:
	poetry run python manage.py shell

# Стандартное создание суперпользователя
superuser:
	poetry run python manage.py createsuperuser

# Наша кастомная команда для наполнения БД
init-data:
	poetry run python manage.py init_data

# ==========================================
# Linters & Formatting
# ==========================================

# Проверка кода линтером Ruff
lint:
	poetry run ruff check .

# Автоматическое форматирование кода (Ruff)
format:
	poetry run ruff check --fix .
	poetry run ruff format .

# ==========================================
# Docker Infrastructure
# ==========================================

# Запуск БД и Redis в фоновом режиме
up:
	docker-compose up -d

# Остановка контейнеров
down:
	docker-compose down

# ==========================================
# Tests
# ==========================================

# Запуск тестов
test:
	poetry run pytest

# ==========================================
# Celery Workers & Beat
# ==========================================

# Воркер для быстрых торговых операций (Очередь 1)
celery-trade:
	poetry run celery -A config worker -Q trading_queue --concurrency=1 --loglevel=info

# Воркер для тяжелых складских операций (Очередь 2) - тоже 1 задача за раз
celery-warehouse:
	poetry run celery -A config worker -Q warehouse_queue --concurrency=1 --loglevel=info

# Планировщик периодических задач (Celery Beat)
celery-beat:
	poetry run celery -A config beat --loglevel=info
