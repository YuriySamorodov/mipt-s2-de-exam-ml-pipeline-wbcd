#!/bin/bash
# PostgreSQL вариант со SequentialExecutor (стабильный)

echo " Запуск Airflow PostgreSQL со SequentialExecutor"

# Остановим старые процессы
pkill -f "airflow scheduler" 2>/dev/null || true
sleep 2

# Активируем окружение
source venv/bin/activate

# Устанавливаем переменные окружения
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__EXECUTOR="SequentialExecutor"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"

echo " Проверка подключения к PostgreSQL..."
airflow db check

if [ $? -eq 0 ]; then
echo " PostgreSQL доступен"

echo " Запуск scheduler (SequentialExecutor)..."
nohup airflow scheduler > logs/scheduler_postgres_sequential.log 2>&1 &
SCHEDULER_PID=$!

echo " Scheduler запущен (PID: $SCHEDULER_PID)"
echo " База данных: PostgreSQL"
echo " Executor: SequentialExecutor" 
echo " Порт: 8082"

# Проверяем через 10 секунд
sleep 10
if ps -p $SCHEDULER_PID > /dev/null; then
echo " Scheduler работает стабильно"
echo " Теперь можно тестировать DAGs в веб-интерфейсе"
else
echo " Scheduler завершился с ошибкой"
tail -10 logs/scheduler_postgres_sequential.log
fi
else
echo " Проблема с подключением к PostgreSQL"
exit 1
fi
