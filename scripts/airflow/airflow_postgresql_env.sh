#!/bin/bash
# Настройки окружения для Airflow с PostgreSQL

# Определяем директорию проекта (где лежит этот скрипт)
# Поддержка как source, так и прямого выполнения
if [[ -n "${BASH_SOURCE[0]}" ]]; then
# Скрипт был вызван через source и BASH_SOURCE доступен
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
# Используем $0 как fallback
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

PROJECT_DIR="$SCRIPT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Устанавливаем AIRFLOW_HOME относительно директории проекта (абсолютный путь)
export AIRFLOW_HOME="$PROJECT_DIR/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql://airflow_user:airflow_password@localhost:5432/airflow_metadata?connect_timeout=60&application_name=airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"

# Удаляем старые переменные окружения (если есть)
unset AIRFLOW__CORE__SQL_ALCHEMY_CONN

echo "Переменные окружения Airflow установлены для PostgreSQL:"
echo "PROJECT_DIR: $PROJECT_DIR"
echo "AIRFLOW_HOME: $AIRFLOW_HOME"
echo "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: $AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
echo "AIRFLOW__CORE__EXECUTOR: $AIRFLOW__CORE__EXECUTOR"
echo ""

# Проверяем наличие виртуального окружения
if [ -d "$PROJECT_DIR/venv" ]; then
echo "Виртуальное окружение найдено: $PROJECT_DIR/venv"
echo "Для активации используйте: source $PROJECT_DIR/venv/bin/activate"
else
echo "ВНИМАНИЕ: Виртуальное окружение не найдено в $PROJECT_DIR/venv"
fi

# Проверяем наличие директории airflow
if [ -d "$AIRFLOW_HOME" ]; then
echo "Директория Airflow найдена: $AIRFLOW_HOME"
else
echo "ВНИМАНИЕ: Директория Airflow не найдена: $AIRFLOW_HOME"
fi

echo ""
echo "Для запуска Airflow выполните:"
echo "1. source $PROJECT_DIR/venv/bin/activate # Активировать виртуальное окружение"
echo "2. airflow scheduler & # Запустить scheduler в фоне"
echo "3. airflow webserver -p 8082 # Запустить webserver на порту 8082 (PostgreSQL)"
