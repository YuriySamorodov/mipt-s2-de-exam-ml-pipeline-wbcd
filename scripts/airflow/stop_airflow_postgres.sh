#!/bin/bash
# Скрипт для остановки Airflow PostgreSQL (порт 8082)

echo " Остановка Airflow PostgreSQL (порт 8082)"

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Остановка процессов по PID файлам
if [ -f "$PROJECT_DIR/logs/scheduler_postgres.pid" ]; then
SCHEDULER_PID=$(cat "$PROJECT_DIR/logs/scheduler_postgres.pid")
echo " Остановка Scheduler (PID: $SCHEDULER_PID)..."
kill $SCHEDULER_PID 2>/dev/null || true
rm -f "$PROJECT_DIR/logs/scheduler_postgres.pid"
fi

if [ -f "$PROJECT_DIR/logs/webserver_postgres.pid" ]; then
WEBSERVER_PID=$(cat "$PROJECT_DIR/logs/webserver_postgres.pid")
echo " Остановка Webserver (PID: $WEBSERVER_PID)..."
kill $WEBSERVER_PID 2>/dev/null || true
rm -f "$PROJECT_DIR/logs/webserver_postgres.pid"
fi

# Принудительная остановка процессов на порту 8082
echo " Поиск и остановка процессов на порту 8082..."
lsof -ti:8082 | xargs kill -9 2>/dev/null || true

# Принудительная остановка всех процессов Airflow
echo " Поиск и остановка всех процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

# Ожидание завершения процессов
sleep 3

echo " Airflow PostgreSQL остановлен (порт 8082)"
echo " Логи сохранены в $PROJECT_DIR/logs/"
