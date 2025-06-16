#!/bin/bash

#  Быстрая настройка Single Repository для Docker Hub
# Автор: ML Pipeline Project

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE} Настройка Single Repository для Docker Hub${NC}"
echo "=================================================="

# Запрос username
read -p "Введите ваш Docker Hub username: " DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED} Username не может быть пустым${NC}"
    exit 1
fi

# Запрос версии
read -p "Введите версию образов (по умолчанию: latest): " VERSION
VERSION=${VERSION:-latest}

# Создание .env файла
echo -e "${BLUE} Создание .env файла...${NC}"
cat > .env << EOF
# Docker Hub настройки
DOCKER_USERNAME=${DOCKER_USERNAME}
VERSION=${VERSION}

# PostgreSQL настройки
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow

# Airflow настройки
AIRFLOW_UID=1001
AIRFLOW_GID=0

# ML Pipeline пути
ML_PIPELINE_DATA_PATH=/opt/airflow/data
ML_PIPELINE_RESULTS_PATH=/opt/airflow/results
EOF

echo -e "${GREEN} Файл .env создан${NC}"

# Проверка Docker login
echo -e "${BLUE} Проверка аутентификации Docker...${NC}"
if ! docker info | grep -q "Username:"; then
    echo -e "${YELLOW}  Требуется аутентификация в Docker Hub${NC}"
    read -p "Выполнить docker login сейчас? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker login
    else
        echo -e "${YELLOW} Выполните 'docker login' перед публикацией${NC}"
    fi
else
    echo -e "${GREEN} Уже авторизованы в Docker Hub${NC}"
fi

# Выбор действия
echo ""
echo -e "${BLUE} Что хотите сделать?${NC}"
echo "1) Собрать образы локально (тестирование)"
echo "2) Собрать и опубликовать в Docker Hub"
echo "3) Только создать .env файл (уже сделано)"
echo "4) Запустить с существующими образами"
echo ""
read -p "Выберите опцию (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        echo -e "${BLUE} Локальная сборка образов...${NC}"
        ./build_and_publish_repo.sh "$VERSION" --username="$DOCKER_USERNAME"
        ;;
    2)
        echo -e "${BLUE} Сборка и публикация в Docker Hub...${NC}"
        ./build_and_publish_repo.sh "$VERSION" --username="$DOCKER_USERNAME" --push
        ;;
    3)
        echo -e "${GREEN} Файл .env уже создан${NC}"
        ;;
    4)
        echo -e "${BLUE} Запуск с существующими образами...${NC}"
        docker-compose -f docker-compose.single-repo.yml up -d
        ;;
    *)
        echo -e "${YELLOW} Неверная опция${NC}"
        exit 1
        ;;
esac

# Итоговая информация
echo ""
echo "=================================================="
echo -e "${GREEN} Настройка завершена!${NC}"
echo ""
echo -e "${BLUE} Параметры конфигурации:${NC}"
echo "  Docker Hub username: ${DOCKER_USERNAME}"
echo "  Версия образов: ${VERSION}"
echo "  .env файл создан"
echo ""
echo -e "${BLUE} Полезные команды:${NC}"
echo "  # Локальная сборка"
echo "  ./build_and_publish_repo.sh ${VERSION} --username=${DOCKER_USERNAME}"
echo ""
echo "  # Публикация в Docker Hub"
echo "  ./build_and_publish_repo.sh ${VERSION} --username=${DOCKER_USERNAME} --push"
echo ""
echo "  # Запуск системы"
echo "  docker-compose -f docker-compose.single-repo.yml up -d"
echo ""
echo "  # Проверка статуса"
echo "  docker-compose -f docker-compose.single-repo.yml ps"
echo ""
echo -e "${BLUE} После публикации пользователи смогут:${NC}"
echo "  docker pull ${DOCKER_USERNAME}/ml-pipeline:airflow-latest"
echo "  docker pull ${DOCKER_USERNAME}/ml-pipeline:postgres-latest"
