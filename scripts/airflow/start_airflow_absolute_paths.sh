#!/bin/bash
# Обновленный скрипт для запуска Airflow с программным формированием абсолютных путей

echo " Запуск Airflow с программным формированием абсолютных путей"
echo " Режим: Разработка/Тестирование (SQLite + SequentialExecutor)"
echo ""

# Определяем директорию проекта программно
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo " Директория проекта: $PROJECT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Проверяем наличие виртуального окружения
if [ ! -d "$PROJECT_DIR/venv" ]; then
echo " Виртуальное окружение не найдено. Создаем..."
python3 ../../-m venv venv
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip

# Устанавливаем Airflow если requirements.txt существует
if [ -f "requirements.txt" ]; then
pip install -r requirements.txt
else
echo " Установка Apache Airflow..."
pip install apache-airflow==2.10.5 apache-airflow-providers-postgres
fi
else
echo " Активация виртуального окружения..."
source "$PROJECT_DIR/venv/bin/activate"
fi

# Проверяем установку Airflow
if ! command -v airflow &> /dev/null; then
echo " Установка Apache Airflow..."
pip install apache-airflow==2.10.5 apache-airflow-providers-postgres
fi

echo " Версия Airflow: $(airflow version)"

# Останавливаем текущие процессы
echo " Остановка текущих процессов Airflow..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# Запускаем скрипт для программного формирования путей и конфигурации
echo " Настройка конфигурации с абсолютными путями..."
python ../../setup_airflow_config.py

# Устанавливаем переменные окружения с абсолютными путями
echo " Установка переменных окружения с абсолютными путями..."
python ../../set_absolute_paths_env.py --generate-script
source set_airflow_env.sh

echo " AIRFLOW_HOME: $AIRFLOW_HOME"

# Создаем директории для логов
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/dags"
mkdir -p "$PROJECT_DIR/plugins"

# Инициализация базы данных с абсолютными путями
echo " Инициализация базы данных с абсолютными путями..."
python ../../init_airflow_with_absolute_paths.py

# Проверяем результат инициализации
if [ $? -ne 0 ]; then
echo " Ошибка инициализации базы данных"
exit 1
fi

echo ""
echo " Запуск сервисов Airflow..."

# Запуск scheduler в фоне
echo " Запуск Scheduler..."
nohup airflow scheduler > "$PROJECT_DIR/logs/scheduler_absolute_paths.log" 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler запущен (PID: $SCHEDULER_PID)"

# Ожидание инициализации scheduler
sleep 5

# Запуск webserver
echo " Запуск Webserver на порту 8081..."
nohup airflow webserver --port 8081 > "$PROJECT_DIR/logs/webserver_absolute_paths.log" 2>&1 &
WEBSERVER_PID=$!
echo " Webserver запущен (PID: $WEBSERVER_PID)"

# Сохранение PID в файлы
echo $SCHEDULER_PID > "$PROJECT_DIR/logs/scheduler_absolute_paths.pid"
echo $WEBSERVER_PID > "$PROJECT_DIR/logs/webserver_absolute_paths.pid"

echo ""
echo " Airflow запущен успешно!"
echo ""
echo " Информация о системе:"
echo " Web UI: http://localhost:8081"
echo " Логин: admin"
echo " Пароль: admin"
echo " База данных: SQLite (абсолютный путь)"
echo " Исполнитель: SequentialExecutor"
echo ""
echo " Логи:"
echo " Scheduler: $PROJECT_DIR/logs/scheduler_absolute_paths.log"
echo " Webserver: $PROJECT_DIR/logs/webserver_absolute_paths.log"
echo ""
echo " Для остановки используйте: ./stop_airflow_absolute_paths.sh"
echo ""
echo "⏳ Ожидание готовности webserver (30 секунд)..."
sleep 30

echo " Проверка готовности сервисов..."
if curl -s http://localhost:8081/health > /dev/null; then
echo " Webserver готов: http://localhost:8081"
else
echo " Webserver все еще запускается, проверьте логи"
echo " Лог webserver:"
tail -n 10 "$PROJECT_DIR/logs/webserver_absolute_paths.log"
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
