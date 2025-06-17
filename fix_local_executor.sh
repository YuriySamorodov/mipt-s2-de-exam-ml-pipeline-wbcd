#!/bin/bash
# Исправление LocalExecutor для macOS

echo " Исправление LocalExecutor для macOS..."

# Останавливаем все процессы Airflow
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
sleep 3

# Устанавливаем переменные окружения для macOS multiprocessing
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
export AIRFLOW__CORE__PARALLELISM="4"
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG="4"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"

# Активируем venv
source venv/bin/activate

echo " Запуск Scheduler с исправленным LocalExecutor..."
nohup airflow scheduler > logs/scheduler_local_fixed.log 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

sleep 5

echo " Запуск Webserver на порту 8082..."
nohup airflow webserver --port 8082 > logs/webserver_local_fixed.log 2>&1 &
WEBSERVER_PID=$!
echo " Webserver запущен (PID: $WEBSERVER_PID)"

echo ""
echo " LocalExecutor настроен для macOS:"
echo " Parallelism: 4"
echo " База данных: PostgreSQL"
echo " Веб-интерфейс: http://localhost:8082"
echo " OBJC_DISABLE_INITIALIZE_FORK_SAFETY: YES"
echo ""
echo " Логи:"
echo " Scheduler: logs/scheduler_local_fixed.log"
echo " Webserver: logs/webserver_local_fixed.log"
