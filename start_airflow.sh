#!/bin/bash
# Скрипт для удобного запуска Airflow с PostgreSQL

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "=== Запуск Airflow ==="
echo "Проект: $PROJECT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Источаем переменные окружения
source "$PROJECT_DIR/airflow_postgresql_env.sh"

# Проверяем наличие виртуального окружения
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "ОШИБКА: Виртуальное окружение не найдено в $PROJECT_DIR/venv"
    echo "Создайте виртуальное окружение: python -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source "$PROJECT_DIR/venv/bin/activate"

# Проверяем установку Airflow
if ! command -v airflow &> /dev/null; then
    echo "ОШИБКА: Airflow не установлен в виртуальном окружении"
    echo "Установите Airflow: pip install apache-airflow"
    exit 1
fi

echo "Версия Airflow: $(airflow version)"
echo ""

# Проверяем соединение с PostgreSQL
echo "Проверка соединения с PostgreSQL..."
if ! airflow db check; then
    echo "ОШИБКА: Не удается подключиться к базе данных PostgreSQL"
    echo "Убедитесь, что PostgreSQL запущен и база данных создана"
    exit 1
fi

echo "Соединение с PostgreSQL успешно!"
echo ""

# Останавливаем существующие процессы Airflow (если есть)
echo "Остановка существующих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
sleep 2

# Запускаем scheduler в фоне
echo "Запуск Airflow Scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler.log" 2>&1 &
SCHEDULER_PID=$!
echo "Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидаем немного для инициализации scheduler
sleep 5

# Запускаем webserver через gunicorn с кастомной конфигурацией
echo "Запуск Airflow Webserver на порту 8080..."
echo "Используется gunicorn с оптимизированными настройками"
echo ""
echo "Для остановки используйте: pkill -f gunicorn"
echo "Web-интерфейс будет доступен по адресу: http://localhost:8080"
echo ""

# Создаем директорию для логов, если не существует
mkdir -p "$PROJECT_DIR/logs"

# Запускаем webserver через gunicorn с нашей конфигурацией
echo "Запуск gunicorn с конфигурацией: $PROJECT_DIR/gunicorn.conf.py"
nohup gunicorn -c "$PROJECT_DIR/gunicorn.conf.py" airflow.www.app:create_app\(\) > "$PROJECT_DIR/logs/webserver.log" 2>&1 &
WEBSERVER_PID=$!

echo "Webserver запущен (PID: $WEBSERVER_PID)"
echo "Логи webserver: $PROJECT_DIR/logs/webserver.log"
echo ""
echo "Ожидание запуска webserver..."
sleep 10

# Проверяем, что webserver запустился
if curl -s -I http://localhost:8080 | grep -q "HTTP"; then
    echo " Webserver успешно запущен и отвечает на порту 8080"
else
    echo " Webserver не отвечает, проверьте логи: $PROJECT_DIR/logs/webserver.log"
fi

echo ""
echo " Airflow готов к работе!"
echo " Web-интерфейс: http://localhost:8080"
echo " Логи scheduler: $PROJECT_DIR/logs/scheduler.log"
echo " Логи webserver: $PROJECT_DIR/logs/webserver.log"
echo ""
echo "Для остановки всех сервисов: pkill -f airflow && pkill -f gunicorn"

# Функция для запуска в режиме разработки
start_dev_mode() {
    echo "=== РЕЖИМ РАЗРАБОТКИ ==="
    echo "Запуск webserver в режиме отладки (без gunicorn)..."
    echo "Web-интерфейс будет доступен по адресу: http://localhost:8080"
    echo ""
    echo "Для остановки нажмите Ctrl+C"
    echo ""
    
    # Запускаем webserver в режиме разработки
    airflow webserver -p 8080 --debug
}

# Проверяем первый аргумент для режима запуска
if [ "$1" = "--dev" ] || [ "$1" = "-d" ]; then
    # Переходим в директорию проекта
    cd "$PROJECT_DIR"
    
    # Источаем переменные окружения
    source "$PROJECT_DIR/airflow_postgresql_env.sh"
    
    # Активируем виртуальное окружение
    source "$PROJECT_DIR/venv/bin/activate"
    
    start_dev_mode
    exit 0
fi
