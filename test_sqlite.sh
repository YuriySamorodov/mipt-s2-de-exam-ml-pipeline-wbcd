#!/bin/bash
# Простой тест SQLite настройки

echo " Тестирование SQLite настройки..."

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/scripts/airflow" && pwd)"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo " PROJECT_DIR: $PROJECT_DIR"
echo " SCRIPT_DIR: $SCRIPT_DIR"

# Активируем venv
echo " Активация venv..."
source "$PROJECT_DIR/venv/bin/activate"
echo " venv активирован"

# Настройка конфигурации SQLite
echo " Настройка SQLite..."
unset AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
cd "$PROJECT_DIR"
python "$SCRIPT_DIR/setup_airflow_config.py"
echo " Настройка завершена"

# Принудительная установка SQLite
export AIRFLOW__CORE__EXECUTOR="SequentialExecutor"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8081"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:///$PROJECT_DIR/airflow/airflow.db"

echo " Переменные окружения:"
echo " AIRFLOW__CORE__EXECUTOR=$AIRFLOW__CORE__EXECUTOR"
echo " AIRFLOW__WEBSERVER__WEB_SERVER_PORT=$AIRFLOW__WEBSERVER__WEB_SERVER_PORT"
echo " AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"

# Инициализация базы данных
echo " Инициализация базы данных..."
python "$SCRIPT_DIR/init_airflow_with_absolute_paths.py"
echo " База данных инициализирована"

echo " Тест завершен успешно!"
