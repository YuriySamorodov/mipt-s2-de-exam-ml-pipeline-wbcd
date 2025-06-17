#!/bin/bash
# Скрипт для остановки Airflow (версия с абсолютными путями)

echo " Остановка Airflow (версия с абсолютными путями)"

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Остановка процессов по PID файлам
if [ -f "$PROJECT_DIR/logs/scheduler_absolute_paths.pid" ]; then
SCHEDULER_PID=$(cat "$PROJECT_DIR/logs/scheduler_absolute_paths.pid")
echo " Остановка Scheduler (PID: $SCHEDULER_PID)..."
kill $SCHEDULER_PID 2>/dev/null || true
rm -f "$PROJECT_DIR/logs/scheduler_absolute_paths.pid"
fi

if [ -f "$PROJECT_DIR/logs/webserver_absolute_paths.pid" ]; then
WEBSERVER_PID=$(cat "$PROJECT_DIR/logs/webserver_absolute_paths.pid")
echo " Остановка Webserver (PID: $WEBSERVER_PID)..."
kill $WEBSERVER_PID 2>/dev/null || true
rm -f "$PROJECT_DIR/logs/webserver_absolute_paths.pid"
fi

# Принудительная остановка всех процессов Airflow
echo " Поиск и остановка всех процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

# Ожидание завершения процессов
sleep 3

echo " Airflow остановлен"
echo " Логи сохранены в $PROJECT_DIR/logs/"
