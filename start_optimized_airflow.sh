#!/bin/bash
# Скрипт для запуска оптимизированного Airflow

set -e

echo " Запуск оптимизированного Airflow с PostgreSQL"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo " Проект: $PROJECT_DIR"

# Активируем виртуальное окружение
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    echo " Активируем виртуальное окружение..."
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo " Виртуальное окружение не найдено в $PROJECT_DIR/venv"
    exit 1
fi

# Загружаем переменные окружения
if [ -f "$PROJECT_DIR/airflow_postgresql_env.sh" ]; then
    echo "  Загружаем переменные окружения..."
    source "$PROJECT_DIR/airflow_postgresql_env.sh"
else
    echo " Файл переменных окружения не найден"
    exit 1
fi

# Проверяем PostgreSQL
echo " Проверяем PostgreSQL..."
if ! brew services list | grep postgresql@14 | grep -q started; then
    echo " Запускаем PostgreSQL..."
    brew services start postgresql@14
    sleep 3
fi

# Проверяем соединение с базой данных
echo " Проверяем соединение с базой данных..."
if ! airflow db check > /dev/null 2>&1; then
    echo " Не удается подключиться к базе данных"
    exit 1
fi

echo " База данных доступна"

# Останавливаем старые процессы
echo " Очищаем старые процессы..."
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "airflow scheduler" 2>/dev/null || true

# Освобождаем порты
echo " Освобождаем порты..."
for port in 8080 8793 8794; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

sleep 2

# Запускаем webserver
echo " Запускаем webserver на порту 8080..."
nohup airflow webserver --port 8080 > "$PROJECT_DIR/airflow/logs/webserver.log" 2>&1 &
WEBSERVER_PID=$!

# Ждем запуска webserver
echo "⏳ Ждем запуска webserver..."
sleep 10

# Запускаем scheduler
echo "⏰ Запускаем scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/airflow/logs/scheduler.log" 2>&1 &
SCHEDULER_PID=$!

# Ждем запуска scheduler
echo "⏳ Ждем запуска scheduler..."
sleep 15

# Проверяем статус
echo ""
echo " Проверяем статус компонентов:"

# Проверяем webserver
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health | grep -q "200"; then
    echo " Webserver: работает (порт 8080)"
else
    echo " Webserver: не отвечает"
fi

# Проверяем scheduler
HEALTH_JSON=$(curl -s http://localhost:8080/api/v1/health 2>/dev/null)
if echo "$HEALTH_JSON" | grep -q '"status": "healthy"' && echo "$HEALTH_JSON" | grep -q 'scheduler'; then
    echo " Scheduler: работает"
else
    echo " Scheduler: не работает"
fi

# Проверяем базу данных
if echo "$HEALTH_JSON" | grep -q '"metadatabase".*"healthy"'; then
    echo " PostgreSQL: подключена"
else
    echo " PostgreSQL: проблемы с подключением"
fi

# Показываем количество процессов PostgreSQL
PG_PROCESSES=$(ps aux | grep postgres | grep -v grep | wc -l)
echo " Процессов PostgreSQL: $PG_PROCESSES (оптимизировано)"

# Показываем PID процессов
echo ""
echo " PID процессов:"
echo "   Webserver: $WEBSERVER_PID"
echo "   Scheduler: $SCHEDULER_PID"

echo ""
echo " Доступные URL:"
echo "   Веб-интерфейс: http://localhost:8080"
echo "   Health API: http://localhost:8080/api/v1/health"

echo ""
echo " Полезные команды:"
echo "   Остановить все: pkill -f 'airflow'"
echo "   Логи webserver: tail -f $PROJECT_DIR/airflow/logs/webserver.log"
echo "   Логи scheduler: tail -f $PROJECT_DIR/airflow/logs/scheduler.log"
echo "   Статус PostgreSQL: brew services list | grep postgresql"

echo ""
echo " Оптимизированный Airflow запущен успешно!"
