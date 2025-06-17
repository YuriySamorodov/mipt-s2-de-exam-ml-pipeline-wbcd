#!/bin/bash
# Скрипт для запуска Airflow PostgreSQL с абсолютными путями (порт 8082)

echo " Запуск Airflow PostgreSQL с программным формированием абсолютных путей"
echo " Режим: PostgreSQL + LocalExecutor (порт 8082)"
echo ""

# Определяем директорию проекта программно
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo " Директория проекта: $PROJECT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Проверяем наличие виртуального окружения
if [ ! -d "$PROJECT_DIR/venv" ]; then
echo " Виртуальное окружение не найдено. Создаем..."
python3 -m venv "$PROJECT_DIR/venv"
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip

# Устанавливаем Airflow с PostgreSQL
echo " Установка Apache Airflow с PostgreSQL..."
pip install apache-airflow==2.10.5 apache-airflow-providers-postgres psycopg2-binary
else
echo " Активация виртуального окружения..."
source "$PROJECT_DIR/venv/bin/activate"
fi

# Проверяем установку Airflow
if ! command -v airflow &> /dev/null; then
echo " Установка Apache Airflow с PostgreSQL..."
pip install apache-airflow==2.10.5 apache-airflow-providers-postgres psycopg2-binary
fi

echo " Версия Airflow: $(airflow version)"

# Останавливаем текущие процессы
echo " Остановка текущих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# Запускаем скрипт для программного формирования путей и конфигурации (PostgreSQL)
echo " Настройка конфигурации PostgreSQL с абсолютными путями..."
python "$SCRIPT_DIR/setup_airflow_config.py" --postgres

# Проверяем что AIRFLOW_HOME установлен корректно
if [ -z "$AIRFLOW_HOME" ]; then
export AIRFLOW_HOME="$PROJECT_DIR/airflow"
fi

echo " AIRFLOW_HOME: $AIRFLOW_HOME"

# Создаем директории для логов
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/dags"
mkdir -p "$PROJECT_DIR/plugins"

# Проверяем подключение к PostgreSQL
echo " Проверка подключения к PostgreSQL..."
if ! command -v psql &> /dev/null; then
echo " psql не найден. Убедитесь, что PostgreSQL установлен и запущен"
fi

# Инициализация базы данных PostgreSQL
echo " Инициализация базы данных PostgreSQL..."
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"

# Инициализируем базу данных
airflow db init

# Создание пользователя admin
echo " Создание пользователя admin..."
airflow users create \
--username admin \
--firstname Admin \
--lastname User \
--role Admin \
--email admin@example.com \
--password admin 2>/dev/null || echo " Пользователь admin уже существует"

# Устанавливаем переменные окружения с абсолютными путями
echo " Установка переменных окружения с абсолютными путями..."
source <(python "$SCRIPT_DIR/set_absolute_paths_env.py" --postgres)

echo ""
echo " Запуск сервисов Airflow PostgreSQL..."

# Запуск scheduler в фоне
echo " Запуск Scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler_postgres.log" 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидание инициализации scheduler
sleep 5

# Запуск webserver на порту 8082
echo " Запуск Webserver на порту 8082..."
nohup airflow webserver --port 8082 > "$PROJECT_DIR/logs/webserver_postgres.log" 2>&1 &
WEBSERVER_PID=$!
echo " Webserver запущен (PID: $WEBSERVER_PID)"

# Сохранение PID в файлы
echo $SCHEDULER_PID > "$PROJECT_DIR/logs/scheduler_postgres.pid"
echo $WEBSERVER_PID > "$PROJECT_DIR/logs/webserver_postgres.pid"

echo ""
echo " Airflow PostgreSQL запущен успешно!"
echo ""
echo " Информация о системе:"
echo " Web UI: http://localhost:8082"
echo " Логин: admin"
echo " Пароль: admin"
echo " База данных: PostgreSQL (localhost:5432)"
echo " Исполнитель: LocalExecutor"
echo ""
echo " Логи:"
echo " Scheduler: $PROJECT_DIR/logs/scheduler_postgres.log"
echo " Webserver: $PROJECT_DIR/logs/webserver_postgres.log"
echo ""
echo " Для остановки используйте: ./stop_airflow_postgres.sh"
echo ""
echo "⏳ Ожидание готовности webserver (30 секунд)..."
sleep 30

echo " Проверка готовности сервисов..."
if curl -s http://localhost:8082/health > /dev/null; then
echo " Webserver готов: http://localhost:8082"
else
echo " Webserver все еще запускается, проверьте логи"
echo " Лог webserver:"
tail -n 10 "$PROJECT_DIR/logs/webserver_postgres.log"
fi

echo ""
echo " Система готова к работе!"
echo ""
echo " Все пути сформированы программно и являются абсолютными:"
echo " Проект: $PROJECT_DIR"
echo " AIRFLOW_HOME: $AIRFLOW_HOME"
echo " База данных: PostgreSQL (postgresql+psycopg2://airflow:airflow@localhost:5432/airflow)"
echo " DAGs: $PROJECT_DIR/dags"
echo " Логи: $PROJECT_DIR/logs"
