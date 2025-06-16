#!/bin/bash
# Скрипт для локальной сборки Docker образа ML Pipeline

echo " Сборка Docker образа ML Pipeline"
echo "===========================================" 

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Переходим в директорию проекта  
cd "$PROJECT_DIR"

# Имя образа
IMAGE_NAME="ml-pipeline-airflow"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo " Информация о сборке:"
echo "    Директория: $PROJECT_DIR"
echo "     Имя образа: $FULL_IMAGE_NAME"
echo "    Dockerfile: Dockerfile.local"
echo ""

# Проверяем наличие необходимых файлов
echo " Проверка необходимых файлов..."

REQUIRED_FILES=(
    "Dockerfile.local"
    "requirements.txt"
    "dags"
    "etl"
    "config"
    "data"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$PROJECT_DIR/$file" ]; then
        echo " Файл/директория не найден: $file"
        exit 1
    else
        echo "    $file"
    fi
done

echo ""
echo " Начинаем сборку образа..."
echo ""

# Сборка Docker образа
docker build \
    -t "$FULL_IMAGE_NAME" \
    -f Dockerfile.local \
    . 

BUILD_EXIT_CODE=$?

echo ""
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo " Сборка образа завершена успешно!"
    echo ""
    
    # Показываем информацию об образе
    echo " Информация о созданном образе:"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo ""
    echo " Образ готов к использованию:"
    echo "     Имя: $FULL_IMAGE_NAME"
    echo "    Запуск: docker-compose up -d"
    echo "    Проверка: docker images | grep $IMAGE_NAME"
    
    echo ""
    echo " Следующие шаги:"
    echo "   1. Запустите: docker-compose up -d"
    echo "   2. Откройте: http://localhost:8080"
    echo "   3. Войдите: admin/admin"
    
else
    echo " Ошибка при сборке образа!"
    echo " Проверьте логи выше для подробностей"
    exit 1
fi

echo ""
echo " Сборка завершена!"
