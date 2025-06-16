#!/bin/bash
# Скрипт для запуска Airflow с PostgreSQL и LocalExecutor
# Используется для production-среды

echo " Запуск Airflow (PostgreSQL + LocalExecutor)"
echo " Режим: Production"
echo " База данных: PostgreSQL"
echo "  Исполнитель: LocalExecutor"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Создаем директории для логов если их нет
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/airflow_home"

# Останавливаем текущие процессы
echo " Остановка текущих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# Загружаем переменные окружения PostgreSQL
if [ -f "$PROJECT_DIR/airflow_postgresql_env.sh" ]; then
    echo " Загрузка конфигурации PostgreSQL..."
    source "$PROJECT_DIR/airflow_postgresql_env.sh"
else
    echo "  Файл airflow_postgresql_env.sh не найден. Используем стандартные настройки..."
    export AIRFLOW_HOME="$PROJECT_DIR/airflow_home"
    export AIRFLOW__CORE__DAGS_FOLDER="$PROJECT_DIR/dags"
    export AIRFLOW__CORE__PLUGINS_FOLDER="$PROJECT_DIR/plugins"
    export AIRFLOW__CORE__EXECUTOR=LocalExecutor
    export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
    export AIRFLOW__CORE__LOAD_EXAMPLES=False
    export AIRFLOW__WEBSERVER__SECRET_KEY="production_secret_key_change_me"
    export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080
    export AIRFLOW__LOGGING__BASE_LOG_FOLDER="$PROJECT_DIR/logs"
fi

# Проверяем наличие виртуального окружения
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "  Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
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
    pip install apache-airflow==2.8.1 psycopg2-binary
fi

echo " Версия Airflow: $(airflow version)"
echo " AIRFLOW_HOME: $AIRFLOW_HOME"
echo " База данных: PostgreSQL"
echo ""

# Проверяем соединение с PostgreSQL
echo " Проверка соединения с PostgreSQL..."
if ! airflow db check; then
    echo " Не удается подключиться к PostgreSQL"
    echo ""
    echo "  Убедитесь что:"
    echo "   1. PostgreSQL запущен"
    echo "   2. База данных 'airflow' создана"
    echo "   3. Пользователь 'airflow' существует с правильным паролем"
    echo ""
    echo " Команды для настройки PostgreSQL:"
    echo "   createdb airflow"
    echo "   createuser -s airflow"
    echo "   psql -c \"ALTER USER airflow PASSWORD 'airflow';\""
    echo ""
    exit 1
fi

echo " Соединение с PostgreSQL успешно!"
echo ""

# Инициализация/обновление базы данных
echo " Инициализация базы данных..."
airflow db migrate

# Создание пользователя admin
echo " Создание пользователя admin..."
airflow users create \
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
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler_postgresql.log" 2>&1 &
SCHEDULER_PID=$!
echo "    Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидание инициализации scheduler
sleep 5

# Запуск webserver через gunicorn для лучшей производительности
echo " Запуск Webserver на порту 8080..."
if [ -f "$PROJECT_DIR/gunicorn.conf.py" ]; then
    nohup gunicorn -c "$PROJECT_DIR/gunicorn.conf.py" airflow.www.app:create_app\(\) > "$PROJECT_DIR/logs/webserver_postgresql.log" 2>&1 &
    WEBSERVER_PID=$!
    echo "    Webserver запущен через Gunicorn (PID: $WEBSERVER_PID)"
else
    nohup airflow webserver --port 8080 > "$PROJECT_DIR/logs/webserver_postgresql.log" 2>&1 &
    WEBSERVER_PID=$!
    echo "    Webserver запущен (PID: $WEBSERVER_PID)"
fi

# Сохранение PID в файлы
echo $SCHEDULER_PID > "$PROJECT_DIR/logs/scheduler_postgresql.pid"
echo $WEBSERVER_PID > "$PROJECT_DIR/logs/webserver_postgresql.pid"

echo ""
echo " Airflow запущен успешно!"
echo ""
echo " Информация о системе:"
echo "    Web UI: http://localhost:8080"
echo "    Логин: admin"
echo "    Пароль: admin"
echo "    База данных: PostgreSQL"
echo "     Исполнитель: LocalExecutor"
echo "    Подключение: $AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
echo ""
echo " Логи:"
echo "    Scheduler: $PROJECT_DIR/logs/scheduler_postgresql.log"
echo "    Webserver: $PROJECT_DIR/logs/webserver_postgresql.log"
echo ""
echo " Для остановки используйте: ./stop_airflow_postgresql.sh"
echo ""
echo "⌛ Ожидание готовности webserver (30 секунд)..."
sleep 30

echo " Проверка готовности сервисов..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo " Webserver готов: http://localhost:8080"
else
    echo " Webserver все еще запускается, проверьте логи"
fi

echo ""
echo " Система готова к работе!"
