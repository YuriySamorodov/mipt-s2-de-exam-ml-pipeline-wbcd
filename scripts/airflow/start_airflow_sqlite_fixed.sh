#!/bin/bash
# Улучшенный скрипт для запуска Airflow с SQLite (обходит проблемы миграций)

echo " Запуск Airflow (SQLite + SequentialExecutor) - Улучшенная версия"
echo " Режим: Разработка/Тестирование"
echo " База данных: SQLite"
echo " Исполнитель: SequentialExecutor"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Создаем директории для логов если их нет
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/airflow"

# Останавливаем текущие процессы
echo " Остановка текущих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# Настройка переменных окружения для SQLite
export AIRFLOW_HOME="$PROJECT_DIR/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$PROJECT_DIR/dags"
export AIRFLOW__CORE__PLUGINS_FOLDER="$PROJECT_DIR/plugins"
export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:///$PROJECT_DIR/airflow/airflow.db"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__WEBSERVER__SECRET_KEY="dev_secret_key_for_sqlite"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8081
export AIRFLOW__LOGGING__BASE_LOG_FOLDER="$PROJECT_DIR/logs"

# Дополнительные настройки для обхода проблем
export AIRFLOW__CORE__CHECK_SLAS=False
export AIRFLOW__CORE__STORE_SERIALIZED_DAGS=True
export AIRFLOW__CORE__STORE_DAG_CODE=True
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
export AIRFLOW__WEBSERVER__WORKERS=1
export AIRFLOW__WEBSERVER__WORKER_TIMEOUT=300

# Проверяем наличие виртуального окружения
if [ ! -d "$PROJECT_DIR/venv" ]; then
echo " Виртуальное окружение не найдено. Создаем..."
python3 ../../-m venv venv
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
else
echo " Активация виртуального окружения..."
source "$PROJECT_DIR/venv/bin/activate"
fi

# Проверяем установку Airflow
if ! command -v airflow &> /dev/null; then
echo " Установка Apache Airflow..."
pip install apache-airflow==2.10.5
fi

echo " Версия Airflow: $(airflow version)"
echo " AIRFLOW_HOME: $AIRFLOW_HOME"
echo " База данных: SQLite"
echo ""

# Инициализация базы данных (с нашим скриптом)
echo " Инициализация базы данных SQLite..."
python ../../fix_airflow_db.py

# Создание пользователя admin (если не существует)
echo " Проверка пользователя admin..."
airflow users create \
--username admin \
--firstname Admin \
--lastname User \
--role Admin \
--email admin@example.com \
--password admin 2>/dev/null || echo " Пользователь admin уже существует"

echo ""
echo " Запуск сервисов Airflow..."

# Запуск scheduler в фоне
echo " Запуск Scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler_sqlite.log" 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидание инициализации scheduler
sleep 5

# Запуск webserver
echo " Запуск Webserver на порту 8081..."
nohup airflow webserver --port 8081 > "$PROJECT_DIR/logs/webserver_sqlite.log" 2>&1 &
WEBSERVER_PID=$!
echo " Webserver запущен (PID: $WEBSERVER_PID)"

# Сохранение PID в файлы
echo $SCHEDULER_PID > "$PROJECT_DIR/logs/scheduler_sqlite.pid"
echo $WEBSERVER_PID > "$PROJECT_DIR/logs/webserver_sqlite.pid"

echo ""
echo " Airflow запущен успешно!"
echo ""
echo " Информация о системе:"
echo " Web UI: http://localhost:8081"
echo " Логин: admin"
echo " Пароль: admin"
echo " База данных: SQLite ($AIRFLOW_HOME/airflow.db)"
echo " Исполнитель: SequentialExecutor"
echo ""
echo " Логи:"
echo " Scheduler: $PROJECT_DIR/logs/scheduler_sqlite.log"
echo " Webserver: $PROJECT_DIR/logs/webserver_sqlite.log"
echo ""
echo " Для остановки используйте: ./stop_airflow_sqlite.sh"
echo ""
echo "⏳ Ожидание готовности webserver (30 секунд)..."
sleep 30

echo " Проверка готовности сервисов..."
if curl -s http://localhost:8081/health > /dev/null; then
echo " Webserver готов: http://localhost:8081"
else
echo " Webserver все еще запускается, проверьте логи"
fi

echo ""
echo " Система готова к работе!"
echo " Для тестирования DAG используйте: python ../../test_airflow_dag.py"
