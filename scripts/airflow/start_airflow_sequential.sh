#!/bin/bash
# Скрипт для запуска Airflow с SequentialExecutor (100% устранение zombie процессов)

echo " Запуск Airflow с SequentialExecutor"
echo " Полное устранение zombie процессов на macOS"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Останавливаем текущие процессы
echo " Остановка текущих процессов Airflow..."
pkill -f airflow 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 3

# Активируем окружение
echo " Активация окружения..."
source "$PROJECT_DIR/venv/bin/activate"
source "$PROJECT_DIR/airflow_postgresql_env.sh"

# Переключаемся на SequentialExecutor
echo " Настройка SequentialExecutor..."
export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
source "$PROJECT_DIR/venv/bin/activate"

echo "Используется SequentialExecutor (без zombie процессов)"
echo ""

# Останавливаем существующие процессы Airflow
echo "Остановка существующих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 2

# Запускаем scheduler в фоне
echo "Запуск Airflow Scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler_sequential.log" 2>&1 &
SCHEDULER_PID=$!
echo "Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидаем немного для инициализации scheduler
sleep 5

# Запускаем webserver через gunicorn
echo "Запуск Airflow Webserver на порту 8081..."
nohup gunicorn -c "$PROJECT_DIR/gunicorn.conf.py" airflow.www.app:create_app\(\) > "$PROJECT_DIR/logs/webserver_sequential.log" 2>&1 &
WEBSERVER_PID=$!

echo "Webserver запущен (PID: $WEBSERVER_PID)"
echo ""
echo " Airflow с SequentialExecutor готов к работе!"
echo " Web-интерфейс: http://localhost:8081"
echo " Логи scheduler: $PROJECT_DIR/logs/scheduler_sequential.log"
echo " Логи webserver: $PROJECT_DIR/logs/webserver_sequential.log"
echo ""
echo " ВНИМАНИЕ: SequentialExecutor выполняет задачи последовательно"
echo " Используйте только для тестирования или простых DAG"
echo ""
echo "Для остановки: pkill -f airflow && pkill -f gunicorn"
