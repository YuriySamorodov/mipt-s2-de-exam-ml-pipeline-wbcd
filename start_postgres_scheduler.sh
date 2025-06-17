#!/bin/bash
# Простой и надежный запуск Airflow Scheduler для PostgreSQL

echo " Запуск Airflow Scheduler (PostgreSQL + LocalExecutor)"

# Остановим старые процессы
pkill -f "airflow scheduler" 2>/dev/null || true
sleep 2

# Активируем окружение
source venv/bin/activate

# Устанавливаем переменные окружения
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"

# Критические настройки для macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYTHONUNBUFFERED=1

# Попробуем сначала с SequentialExecutor, потом переключим на LocalExecutor
echo " Тестовый запуск с SequentialExecutor..."
export AIRFLOW__CORE__EXECUTOR="SequentialExecutor"

# Проверим подключение к БД
echo " Проверка подключения к базе данных..."
airflow db check

if [ $? -eq 0 ]; then
echo " База данных доступна"

# Переключаемся на LocalExecutor
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"

echo " Запуск scheduler с LocalExecutor..."
nohup airflow scheduler > logs/scheduler_simple.log 2>&1 &
SCHEDULER_PID=$!

echo " Scheduler запущен (PID: $SCHEDULER_PID)"

# Ждем немного и проверяем
sleep 5
if ps -p $SCHEDULER_PID > /dev/null; then
echo " Scheduler работает стабильно"
else
echo " Scheduler завершился с ошибкой"
echo " Последние 10 строк лога:"
tail -10 logs/scheduler_simple.log
fi
else
echo " Проблема с подключением к базе данных"
exit 1
fi
