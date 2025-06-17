#!/bin/bash
# Скрипт для запуска Airflow с SQLite и SequentialExecutor
# Используется для разработки и тестирования

echo " Запуск Airflow (SQLite + SequentialExecutor)"
echo " Режим: Разработка/Тестирование"
echo " База данных: SQLite"
echo " Исполнитель: SequentialExecutor"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Активируем виртуальное окружение
source "$PROJECT_DIR/scripts/activate_venv.sh"

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

# Проверяем установку Airflow в виртуальном окружении
if ! $VENV_PYTHON -c "import airflow" &> /dev/null; then
echo " Установка Apache Airflow в виртуальное окружение..."
$VENV_PIP install apache-airflow==2.8.1
fi

echo " Версия Airflow: $($VENV_PYTHON -m airflow version)"
echo " AIRFLOW_HOME: $AIRFLOW_HOME"
echo " База данных: SQLite"
echo ""

# Инициализация базы данных
echo "️ Инициализация базы данных SQLite..."
$VENV_PYTHON -m airflow db init

# Создание пользователя admin
echo " Создание пользователя admin..."
$VENV_PYTHON -m airflow users create \
--username admin \
--firstname Admin \
--lastname User \
--role Admin \
--email admin@example.com \
--password admin 2>/dev/null || echo "Пользователь admin уже существует"

echo ""
echo " Запуск сервисов Airflow..."

# Запуск scheduler в фоне
echo " Запуск Scheduler..."
nohup $VENV_PYTHON -m airflow scheduler > "$PROJECT_DIR/logs/scheduler_sqlite.log" 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидание инициализации scheduler
sleep 5

# Запуск webserver
echo " Запуск Webserver на порту 8081..."
nohup $VENV_PYTHON -m airflow webserver --port 8081 > "$PROJECT_DIR/logs/webserver_sqlite.log" 2>&1 &
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
echo "⌛ Ожидание готовности webserver (30 секунд)..."
sleep 30

echo " Проверка готовности сервисов..."
if curl -s http://localhost:8081/health > /dev/null; then
echo " Webserver готов: http://localhost:8081"
else
echo " Webserver все еще запускается, проверьте логи"
fi

echo ""
echo " Система готова к работе!"
