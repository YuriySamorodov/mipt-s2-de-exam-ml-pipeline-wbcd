#!/bin/bash
# Скрипт для остановки Airflow Docker (порт 8083)

echo " Остановка Airflow Docker (порт 8083)"

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

echo " Остановка Docker контейнеров..."
docker-compose down

echo " Остановка процессов на порту 8083..."
lsof -ti:8083 | xargs kill -9 2>/dev/null || true

echo " Очистка контейнеров (опционально)..."
read -p "Удалить контейнеры и образы? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
docker-compose down --volumes --remove-orphans
docker system prune -f
echo "️ Контейнеры и образы удалены"
fi

echo " Airflow Docker остановлен (порт 8083)"
echo " Логи сохранены в $PROJECT_DIR/logs/"
