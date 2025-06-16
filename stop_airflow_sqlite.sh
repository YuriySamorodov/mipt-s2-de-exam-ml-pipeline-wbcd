#!/bin/bash
# Скрипт для остановки Airflow с SQLite

echo " Остановка Airflow (SQLite режим)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Остановка по PID файлам
if [ -f "$PROJECT_DIR/logs/scheduler_sqlite.pid" ]; then
    SCHEDULER_PID=$(cat "$PROJECT_DIR/logs/scheduler_sqlite.pid")
    echo " Остановка Scheduler (PID: $SCHEDULER_PID)..."
    kill $SCHEDULER_PID 2>/dev/null || true
    rm -f "$PROJECT_DIR/logs/scheduler_sqlite.pid"
fi

if [ -f "$PROJECT_DIR/logs/webserver_sqlite.pid" ]; then
    WEBSERVER_PID=$(cat "$PROJECT_DIR/logs/webserver_sqlite.pid")
    echo " Остановка Webserver (PID: $WEBSERVER_PID)..."
    kill $WEBSERVER_PID 2>/dev/null || true
    rm -f "$PROJECT_DIR/logs/webserver_sqlite.pid"
fi

# Принудительная остановка всех процессов Airflow
echo " Принудительная остановка всех процессов..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn.*airflow" 2>/dev/null || true

echo " Airflow (SQLite режим) остановлен"
