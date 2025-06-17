#!/bin/bash
# Скрипт для запуска Airflow SQLite с абсолютными путями (порт 8081)

echo " Запуск Airflow SQLite с программным формированием абсолютных путей"
echo " Режим: SQLite + SequentialExecutor (порт 8081)"
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

# Устанавливаем Airflow если requirements.txt существует
if [ -f "$PROJECT_DIR/config/requirements.txt" ]; then
pip install -r "$PROJECT_DIR/config/requirements.txt"
else
echo " Установка Apache Airflow..."
pip install apache-airflow==2.10.5
fi
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

# Останавливаем текущие процессы
echo " Остановка текущих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# Запускаем скрипт для программного формирования путей и конфигурации (SQLite)
echo " Настройка конфигурации SQLite с абсолютными путями..."
# Убеждаемся, что используется SQLite режим (без --postgres и --docker флагов)
unset AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
python "$SCRIPT_DIR/setup_airflow_config.py"

# Проверяем что AIRFLOW_HOME установлен корректно
if [ -z "$AIRFLOW_HOME" ]; then
export AIRFLOW_HOME="$PROJECT_DIR/airflow"
fi

echo " AIRFLOW_HOME: $AIRFLOW_HOME"

# Создаем директории для логов
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/dags"
mkdir -p "$PROJECT_DIR/plugins"

# Инициализация базы данных с абсолютными путями
echo " Инициализация базы данных SQLite с абсолютными путями..."
python "$SCRIPT_DIR/init_airflow_with_absolute_paths.py"

# Проверяем результат инициализации
if [ $? -ne 0 ]; then
echo " Ошибка инициализации базы данных"
exit 1
fi

# Устанавливаем переменные окружения с абсолютными путями
echo " Установка переменных окружения с абсолютными путями..."
source <(python "$SCRIPT_DIR/set_absolute_paths_env.py")

# Настройка SequentialExecutor для SQLite
export AIRFLOW__CORE__EXECUTOR="SequentialExecutor"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8081"
# Принудительно устанавливаем SQLite подключение
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:///$PROJECT_DIR/airflow/airflow.db"

echo ""
echo " Запуск сервисов Airflow SQLite..."

# Запуск scheduler в фоне
echo " Запуск Scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler_sqlite.log" 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидание инициализации scheduler
sleep 5

# Запуск webserver на порту 8081
echo " Запуск Webserver на порту 8081..."
nohup airflow webserver --port 8081 > "$PROJECT_DIR/logs/webserver_sqlite.log" 2>&1 &
WEBSERVER_PID=$!
echo " Webserver запущен (PID: $WEBSERVER_PID)"

# Сохранение PID в файлы
echo $SCHEDULER_PID > "$PROJECT_DIR/logs/scheduler_sqlite.pid"
echo $WEBSERVER_PID > "$PROJECT_DIR/logs/webserver_sqlite.pid"

echo ""
echo " Airflow SQLite запущен успешно!"
echo ""
echo " Информация о системе:"
echo " Web UI: http://localhost:8081"
echo " Логин: admin"
echo " Пароль: admin"
echo " База данных: SQLite (абсолютный путь)"
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
echo " Лог webserver:"
tail -n 10 "$PROJECT_DIR/logs/webserver_sqlite.log"
fi

echo ""
echo " Система готова к работе!"
echo ""
echo " Все пути сформированы программно и являются абсолютными:"
echo " Проект: $PROJECT_DIR"
echo " AIRFLOW_HOME: $AIRFLOW_HOME"
echo " База данных: $AIRFLOW_HOME/airflow.db"
echo " DAGs: $PROJECT_DIR/dags"
echo " Логи: $PROJECT_DIR/logs"
echo ""
echo " Для тестирования DAG используйте: python ../../test_airflow_dag.py"
