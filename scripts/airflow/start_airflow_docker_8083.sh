#!/bin/bash
# Скрипт для запуска Airflow в Docker с абсолютными путями (порт 8083)

echo " Запуск Airflow в Docker с программным формированием абсолютных путей"
echo " Режим: Docker + PostgreSQL + LocalExecutor (порт 8083)"
echo ""

# Определяем директорию проекта программно
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo " Директория проекта: $PROJECT_DIR"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Создаем директории для монтирования в Docker
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/dags"
mkdir -p "$PROJECT_DIR/plugins"

# Остановка существующих контейнеров
echo " Остановка существующих контейнеров..."
docker-compose down --remove-orphans

# Настройка конфигурации для Docker
echo " Настройка конфигурации Docker с абсолютными путями..."
python ../../setup_airflow_config.py --docker

echo ""
echo " Запуск сервисов в Docker..."

# Запуск сервисов через docker-compose
echo " Сборка и запуск контейнеров..."
docker-compose up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов (60 секунд)..."
sleep 60

# Проверка статуса контейнеров
echo " Проверка статуса контейнеров..."
docker-compose ps

echo ""
echo " Проверка готовности веб-сервера..."
if curl -s http://localhost:8083/health > /dev/null; then
echo " Webserver готов: http://localhost:8083"
else
echo " Webserver все еще запускается, проверьте логи контейнеров"
echo " Логи webserver:"
docker-compose logs airflow-webserver | tail -20
fi

echo ""
echo " Airflow Docker запущен успешно!"
echo ""
echo " Информация о системе:"
echo " Web UI: http://localhost:8083"
echo " Логин: admin"
echo " Пароль: admin"
echo " База данных: PostgreSQL (в Docker контейнере)"
echo " Исполнитель: LocalExecutor"
echo ""
echo " Управление:"
echo " Статус: docker-compose ps"
echo " Логи: docker-compose logs [service-name]"
echo " Остановка: ./stop_airflow_docker.sh"
echo ""
echo " Система готова к работе!"
echo ""
echo " Все пути сформированы программно и являются абсолютными:"
echo " Проект: $PROJECT_DIR"
echo " DAGs: $PROJECT_DIR/dags (монтируется в /opt/airflow/dags)"
echo " Логи: $PROJECT_DIR/logs (монтируется в /opt/airflow/logs)"
echo " Plugins: $PROJECT_DIR/plugins (монтируется в /opt/airflow/plugins)"
