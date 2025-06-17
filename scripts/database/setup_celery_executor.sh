#!/bin/bash
# Скрипт для настройки CeleryExecutor (альтернатива LocalExecutor)

echo " Настройка CeleryExecutor для решения zombie процессов"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo " Проект: $PROJECT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Проверяем наличие Redis
if ! command -v redis-server &> /dev/null; then
echo " Redis не установлен. Устанавливаем через Homebrew..."
if command -v brew &> /dev/null; then
brew install redis
else
echo " Homebrew не найден. Установите Redis вручную:"
echo " https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/"
exit 1
fi
fi

# Запускаем Redis
echo " Запуск Redis..."
redis-server --daemonize yes

# Устанавливаем дополнительные зависимости
echo " Установка Celery зависимостей..."
source "$PROJECT_DIR/venv/bin/activate"
pip install "apache-airflow[celery]" redis

# Обновляем конфигурацию Airflow
echo " Обновление конфигурации для CeleryExecutor..."

# Источаем переменные окружения
source "$PROJECT_DIR/airflow_postgresql_env.sh"

# Устанавливаем CeleryExecutor
export AIRFLOW__CORE__EXECUTOR=CeleryExecutor
export AIRFLOW__CELERY__BROKER_URL=redis://localhost:6379/0
export AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow_user:airflow_password@localhost:5432/airflow_metadata

echo " CeleryExecutor настроен!"
echo ""
echo " Для запуска выполните:"
echo "1. source ./airflow_postgresql_env.sh"
echo "2. export AIRFLOW__CORE__EXECUTOR=CeleryExecutor"
echo "3. export AIRFLOW__CELERY__BROKER_URL=redis://localhost:6379/0"
echo "4. export AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow_user:airflow_password@localhost:5432/airflow_metadata"
echo "5. source venv/bin/activate"
echo "6. airflow scheduler &"
echo "7. airflow celery worker &"
echo "8. airflow webserver -p 8082"
echo ""
echo " Проверка статуса Redis:"
echo " redis-cli ping"
echo ""
echo " Остановка Redis:"
echo " redis-cli shutdown"
