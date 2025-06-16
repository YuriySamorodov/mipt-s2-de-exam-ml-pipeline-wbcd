#!/bin/bash

#  Скрипт для сборки и публикации двух образов в один Docker Hub репозиторий
# Автор: ML Pipeline Project
# Использование: ./build_and_publish_repo.sh [версия] [--push]

set -e

# Конфигурация
REPO_NAME="mipt-s2-de-ml-pipeline"
VERSION="latest"
PUSH_TO_REGISTRY=false
DOCKER_USERNAME=${DOCKER_USERNAME:-"yourusername"}

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Обработка аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH_TO_REGISTRY=true
            shift
            ;;
        --username=*)
            DOCKER_USERNAME="${1#*=}"
            shift
            ;;
        --username)
            DOCKER_USERNAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Использование: $0 [версия] [опции]"
            echo ""
            echo "Опции:"
            echo "  --push                   Отправить образы в Docker Hub"
            echo "  --username=USERNAME     Docker Hub username (по умолчанию: $DOCKER_USERNAME)"
            echo "  --username USERNAME     Docker Hub username (альтернативный синтаксис)"
            echo "  -h, --help              Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  $0                                    # Локальная сборка"
            echo "  $0 v1.0.0                           # Сборка версии v1.0.0"
            echo "  $0 latest --push                     # Сборка и публикация"
            echo "  $0 --username=myusername --push      # С кастомным username"
            echo "  $0 --username myusername v1.0.0 --push # Альтернативный синтаксис"
            exit 0
            ;;
        -*)
            echo "Неизвестная опция: $1"
            exit 1
            ;;
        *)
            # Если это не опция, то это версия
            if [[ "$VERSION" == "latest" ]]; then
                VERSION="$1"
            fi
            shift
            ;;
    esac
done

echo -e "${BLUE} Сборка образов для репозитория ${DOCKER_USERNAME}/${REPO_NAME}${NC}"
echo "=================================================="

# Образы для сборки
IMAGES=(
    "airflow:Dockerfile.local"
    "postgres:Dockerfile.postgres"
)

# Функция для сборки образа
build_image() {
    local image_name=$1
    local dockerfile=$2
    local full_tag="${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-${VERSION}"
    local latest_tag="${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-latest"
    
    echo -e "${BLUE} Сборка ${image_name}...${NC}"
    echo "  Dockerfile: ${dockerfile}"
    echo "  Tag: ${full_tag}"
    
    # Сборка образа
    if docker build -f "${dockerfile}" -t "${full_tag}" .; then
        echo -e "${GREEN} Образ ${full_tag} собран успешно${NC}"
        
        # Тегирование как latest если версия не latest
        if [ "${VERSION}" != "latest" ]; then
            docker tag "${full_tag}" "${latest_tag}"
            echo -e "${GREEN} Создан тег: ${latest_tag}${NC}"
        fi
        
        return 0
    else
        echo -e "${RED} Ошибка сборки образа ${image_name}${NC}"
        return 1
    fi
}

# Функция для публикации образа
push_image() {
    local image_name=$1
    local full_tag="${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-${VERSION}"
    local latest_tag="${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-latest"
    
    echo -e "${BLUE} Публикация ${image_name}...${NC}"
    
    # Публикация основного тега
    if docker push "${full_tag}"; then
        echo -e "${GREEN} Опубликован: ${full_tag}${NC}"
        
        # Публикация latest тега
        if [ "${VERSION}" != "latest" ]; then
            docker push "${latest_tag}"
            echo -e "${GREEN} Опубликован: ${latest_tag}${NC}"
        fi
        
        return 0
    else
        echo -e "${RED} Ошибка публикации ${image_name}${NC}"
        return 1
    fi
}

# Проверка аутентификации (если нужна публикация)
if [ "$PUSH_TO_REGISTRY" = true ]; then
    echo -e "${YELLOW} Проверка аутентификации в Docker Hub...${NC}"
    if ! docker info | grep -q "Username:"; then
        echo -e "${YELLOW}  Не авторизованы в Docker Hub. Выполните: docker login${NC}"
        read -p "Войти в Docker Hub сейчас? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker login
        else
            echo -e "${RED} Публикация невозможна без аутентификации${NC}"
            exit 1
        fi
    fi
fi

# Показать план сборки
echo ""
echo -e "${BLUE} План сборки:${NC}"
echo "  Репозиторий: ${DOCKER_USERNAME}/${REPO_NAME}"
echo "  Версия: ${VERSION}"
for image_info in "${IMAGES[@]}"; do
    IFS=':' read -r image_name dockerfile <<< "$image_info"
    echo "  • ${image_name}: ${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-${VERSION}"
done

if [ "$PUSH_TO_REGISTRY" = true ]; then
    echo "  Публикация:  Да"
else
    echo "  Публикация:  Нет (только локальная сборка)"
fi

echo ""
read -p "Продолжить? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW} Сборка отменена${NC}"
    exit 0
fi

# Сборка образов
echo ""
echo -e "${BLUE} Начало сборки образов...${NC}"
success_count=0
total_count=${#IMAGES[@]}

for image_info in "${IMAGES[@]}"; do
    IFS=':' read -r image_name dockerfile <<< "$image_info"
    
    echo ""
    if build_image "$image_name" "$dockerfile"; then
        ((success_count++))
    fi
done

# Проверка результатов сборки
if [ $success_count -eq $total_count ]; then
    echo ""
    echo -e "${GREEN} Все образы собраны успешно! (${success_count}/${total_count})${NC}"
else
    echo ""
    echo -e "${RED} Ошибки при сборке образов (${success_count}/${total_count})${NC}"
    exit 1
fi

# Публикация (если запрошена)
if [ "$PUSH_TO_REGISTRY" = true ]; then
    echo ""
    echo -e "${BLUE} Публикация образов в Docker Hub...${NC}"
    push_success_count=0
    
    for image_info in "${IMAGES[@]}"; do
        IFS=':' read -r image_name dockerfile <<< "$image_info"
        
        echo ""
        if push_image "$image_name"; then
            ((push_success_count++))
        fi
    done
    
    if [ $push_success_count -eq $total_count ]; then
        echo ""
        echo -e "${GREEN} Все образы опубликованы успешно!${NC}"
    else
        echo ""
        echo -e "${RED} Ошибки при публикации образов (${push_success_count}/${total_count})${NC}"
        exit 1
    fi
fi

# Итоговый отчет
echo ""
echo "=================================================="
echo -e "${GREEN} Готово!${NC}"
echo ""
echo -e "${BLUE} Созданные образы:${NC}"
for image_info in "${IMAGES[@]}"; do
    IFS=':' read -r image_name dockerfile <<< "$image_info"
    echo "  ${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-${VERSION}"
    if [ "${VERSION}" != "latest" ]; then
        echo "  ${DOCKER_USERNAME}/${REPO_NAME}:${image_name}-latest"
    fi
done

echo ""
echo -e "${BLUE} Использование:${NC}"
echo ""
echo "Создайте docker-compose.yml:"
cat << EOF
version: '3.8'
services:
  postgres:
    image: ${DOCKER_USERNAME}/${REPO_NAME}:postgres-${VERSION}
    environment:
      POSTGRES_DB: airflow
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  airflow:
    image: ${DOCKER_USERNAME}/${REPO_NAME}:airflow-${VERSION}
    depends_on:
      - postgres
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    ports:
      - "8080:8080"
    volumes:
      - airflow_logs:/opt/airflow/logs

volumes:
  postgres_data:
  airflow_logs:
EOF

echo ""
echo -e "${BLUE} Команды для скачивания:${NC}"
echo "docker pull ${DOCKER_USERNAME}/${REPO_NAME}:airflow-${VERSION}"
echo "docker pull ${DOCKER_USERNAME}/${REPO_NAME}:postgres-${VERSION}"
