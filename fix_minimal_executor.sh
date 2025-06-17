#!/bin/bash
# Окончательное исправление LocalExecutor для macOS

echo " Окончательное исправление LocalExecutor для macOS..."

# Экспортируем все необходимые переменные
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYTHONUNBUFFERED=1
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor" 
export AIRFLOW__CORE__PARALLELISM="1"
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG="1"
export AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG="1"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"

# Активируем venv
source venv/bin/activate

# Устанавливаем start method через Python
python3 -c "
import multiprocessing
import os
if hasattr(multiprocessing, 'set_start_method'):
try:
multiprocessing.set_start_method('spawn', force=True)
print(' Start method установлен: spawn')
except RuntimeError:
print(' Start method уже установлен')
"

echo " Запуск с минимальным parallelism..."
echo " Parallelism: 1 (минимальный)"
echo " Max tasks per DAG: 1"
echo " Start method: spawn"

# Запускаем scheduler
PYTHONPATH="$PWD:$PYTHONPATH" nohup airflow scheduler > logs/scheduler_minimal.log 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

sleep 10

# Запускаем webserver 
PYTHONPATH="$PWD:$PYTHONPATH" nohup airflow webserver --port 8082 > logs/webserver_minimal.log 2>&1 &
WEBSERVER_PID=$!
echo " Webserver запущен (PID: $WEBSERVER_PID)"

echo ""
echo " Minimal LocalExecutor настроен:"
echo " Parallelism: 1 (последовательное выполнение)"
echo " База данных: PostgreSQL" 
echo " Веб-интерфейс: http://localhost:8082"
echo ""
echo " Проверьте логи через 30 секунд:"
echo " tail -f logs/scheduler_minimal.log"
echo " tail -f logs/webserver_minimal.log"
