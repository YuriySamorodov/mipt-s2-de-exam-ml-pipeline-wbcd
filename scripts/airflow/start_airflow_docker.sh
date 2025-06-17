#!/bin/bash
# Скрипт для запуска оптимизированного Airflow через Docker (решение zombie процессов на macOS)

echo " Запуск оптимизированного Airflow через Docker"
echo " Решение для устранения zombie процессов на macOS + LocalExecutor"
echo ""

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
echo " Docker не установлен. Установите Docker Desktop для macOS"
echo " https://docs.docker.com/desktop/install/mac-install/"
exit 1
fi

if ! command -v docker-compose &> /dev/null; then
echo " Docker Compose не установлен"
exit 1
fi

echo " Docker найден"

# Переходим в директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo " Рабочая директория: $SCRIPT_DIR"

# Останавливаем локальные процессы Airflow (если запущены)
echo " Остановка локальных процессов Airflow..."
pkill -f airflow 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

# Останавливаем старые Docker контейнеры
echo " Остановка старых Docker контейнеров..."
docker-compose down --remove-orphans 2>/dev/null || true

# Создаем необходимые директории
echo " Создание директорий..."
mkdir -p logs results models preprocessors metrics config plugins
mkdir -p data/outputs results/data_quality results/models

# Устанавливаем переменные окружения для Docker
export AIRFLOW_UID=$(id -u)
export AIRFLOW_PROJ_DIR="$SCRIPT_DIR"

echo " Переменные окружения:"
echo " AIRFLOW_UID: $AIRFLOW_UID"
echo " AIRFLOW_PROJ_DIR: $AIRFLOW_PROJ_DIR"

# Проверяем docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
echo " Файл docker-compose.yml не найден"
exit 1
fi

echo " Конфигурация найдена"

# Запускаем инициализацию базы данных
echo " Инициализация базы данных..."
docker-compose up airflow-init

# Запускаем сервисы
echo " Запуск Airflow сервисов..."
docker-compose up -d postgres airflow-webserver airflow-scheduler

echo ""
echo "⏳ Ожидание запуска сервисов..."
sleep 20

# Проверяем статус сервисов
echo " Статус контейнеров:"
docker-compose ps

echo ""
echo " Проверка здоровья Airflow..."
sleep 10

# Проверяем доступность webserver
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8083 | grep -q "200\|302"; then
echo " Webserver доступен на http://localhost:8083"
else
echo " Webserver еще загружается..."
fi

echo ""
echo " Airflow запущен через Docker с оптимизациями!"
echo ""
echo " Web-интерфейс: http://localhost:8083"
echo " Логин: admin / Пароль: admin"
echo ""
echo " Полезные команды:"
echo " docker-compose ps # Статус контейнеров"
echo " docker-compose logs airflow-scheduler # Логи scheduler"
echo " docker-compose logs airflow-webserver # Логи webserver"
echo " docker-compose down # Остановка всех сервисов"
echo " docker-compose exec airflow-scheduler airflow dags list # Список DAG"
echo ""
echo " Мониторинг zombie процессов:"
echo " docker-compose logs airflow-scheduler | grep -i zombie"
echo ""
echo " Docker Airflow с LocalExecutor готов к использованию!"
