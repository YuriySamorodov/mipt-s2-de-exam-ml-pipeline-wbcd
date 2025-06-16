#!/bin/bash

#  Улучшенный скрипт сборки Docker-образа с поддержкой мультиплатформенности
# Автор: ML Pipeline Project
# Использование: ./build_docker_multiplatform.sh [версия] [--platforms]

set -e

# Конфигурация
IMAGE_NAME="ml-pipeline-airflow"
VERSION=${1:-"latest"}
DEFAULT_PLATFORMS="linux/amd64,linux/arm64"
PLATFORMS=""
PUSH_TO_REGISTRY=false
LOAD_LOCAL=true

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Обработка аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        --platforms=*)
            PLATFORMS="${1#*=}"
            shift
            ;;
        --push)
            PUSH_TO_REGISTRY=true
            LOAD_LOCAL=false
            shift
            ;;
        --load)
            LOAD_LOCAL=true
            shift
            ;;
        -h|--help)
            echo "Использование: $0 [версия] [опции]"
            echo ""
            echo "Опции:"
            echo "  --platforms PLATFORMS    Целевые платформы (по умолчанию: linux/amd64,linux/arm64)"
            echo "  --push                   Отправить в реестр вместо локальной загрузки"
            echo "  --load                   Загрузить в локальный Docker (по умолчанию)"
            echo "  -h, --help              Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  $0                                    # Сборка для текущей платформы"
            echo "  $0 --platforms linux/amd64           # Только для AMD64"
            echo "  $0 --platforms linux/amd64,linux/arm64 --push  # Мультиплатформенная сборка с отправкой"
            exit 0
            ;;
        *)
            if [[ -z "$VERSION" ]]; then
                VERSION="$1"
            fi
            shift
            ;;
    esac
done

# Установка платформ по умолчанию
if [[ -z "$PLATFORMS" ]]; then
    PLATFORMS="$DEFAULT_PLATFORMS"
fi

echo -e "${BLUE} Сборка Docker-образа ${IMAGE_NAME}:${VERSION}${NC}"
echo "=================================================="

# Определение текущей архитектуры
CURRENT_ARCH=$(uname -m)
case $CURRENT_ARCH in
    x86_64)
        CURRENT_PLATFORM="linux/amd64"
        ;;
    arm64|aarch64)
        CURRENT_PLATFORM="linux/arm64"
        ;;
    *)
        CURRENT_PLATFORM="linux/amd64"
        echo -e "${YELLOW}  Неизвестная архитектура $CURRENT_ARCH, используем linux/amd64${NC}"
        ;;
esac

echo -e "${BLUE}  Текущая платформа: ${CURRENT_PLATFORM}${NC}"
echo -e "${BLUE} Целевые платформы: ${PLATFORMS}${NC}"

# Проверка Docker Buildx
if ! docker buildx version >/dev/null 2>&1; then
    echo -e "${RED} Docker Buildx не установлен${NC}"
    echo -e "${YELLOW} Установите Docker Desktop или включите экспериментальные функции${NC}"
    exit 1
fi

# Создание или использование существующего builder
BUILDER_NAME="ml-pipeline-builder"
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    echo -e "${BLUE} Создание нового builder: ${BUILDER_NAME}${NC}"
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --use
else
    echo -e "${BLUE} Использование существующего builder: ${BUILDER_NAME}${NC}"
    docker buildx use "$BUILDER_NAME"
fi

# Запуск builder если не запущен
docker buildx inspect --bootstrap

# Проверка Dockerfile
DOCKERFILE="Dockerfile.local"
if [[ ! -f "$DOCKERFILE" ]]; then
    echo -e "${RED} Dockerfile не найден: ${DOCKERFILE}${NC}"
    exit 1
fi

echo -e "${BLUE} Использование Dockerfile: ${DOCKERFILE}${NC}"

# Подготовка тегов
TAGS=(
    "${IMAGE_NAME}:${VERSION}"
)

if [[ "$VERSION" != "latest" ]]; then
    TAGS+=("${IMAGE_NAME}:latest")
fi

# Построение команды сборки
BUILD_ARGS=""
for tag in "${TAGS[@]}"; do
    BUILD_ARGS="$BUILD_ARGS --tag $tag"
done

BUILD_ARGS="$BUILD_ARGS --platform $PLATFORMS"
BUILD_ARGS="$BUILD_ARGS --file $DOCKERFILE"

if [[ "$PUSH_TO_REGISTRY" == "true" ]]; then
    BUILD_ARGS="$BUILD_ARGS --push"
    echo -e "${YELLOW} Образ будет отправлен в реестр${NC}"
elif [[ "$LOAD_LOCAL" == "true" ]]; then
    # Для локальной загрузки можем использовать только одну платформу
    if [[ "$PLATFORMS" == *","* ]]; then
        echo -e "${YELLOW}  Мультиплатформенная сборка не может быть загружена локально${NC}"
        echo -e "${YELLOW} Используем только текущую платформу: ${CURRENT_PLATFORM}${NC}"
        BUILD_ARGS=$(echo "$BUILD_ARGS" | sed "s/--platform [^ ]*/--platform $CURRENT_PLATFORM/")
    fi
    BUILD_ARGS="$BUILD_ARGS --load"
    echo -e "${BLUE} Образ будет загружен в локальный Docker${NC}"
fi

# Показать информацию о сборке
echo ""
echo -e "${BLUE} Параметры сборки:${NC}"
echo -e "  Образ: ${IMAGE_NAME}:${VERSION}"
echo -e "  Платформы: ${PLATFORMS}"
echo -e "  Dockerfile: ${DOCKERFILE}"
echo -e "  Режим: $([ "$PUSH_TO_REGISTRY" == "true" ] && echo "Push to registry" || echo "Load locally")"

echo ""
read -p "Продолжить сборку? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW} Сборка отменена${NC}"
    exit 0
fi

# Запуск сборки
echo ""
echo -e "${BLUE} Запуск сборки...${NC}"
echo "docker buildx build $BUILD_ARGS ."

if docker buildx build $BUILD_ARGS .; then
    echo ""
    echo -e "${GREEN} Сборка завершена успешно!${NC}"
    
    if [[ "$LOAD_LOCAL" == "true" ]]; then
        echo ""
        echo -e "${BLUE} Информация об образе:${NC}"
        docker images | grep "$IMAGE_NAME" | head -5
        
        echo ""
        echo -e "${BLUE} Проверка образа:${NC}"
        docker run --rm "${IMAGE_NAME}:${VERSION}" airflow version
    fi
    
    echo ""
    echo -e "${GREEN} Готово! Образ ${IMAGE_NAME}:${VERSION} собран успешно${NC}"
    
    if [[ "$PUSH_TO_REGISTRY" == "true" ]]; then
        echo -e "${BLUE} Образ отправлен в реестр${NC}"
    else
        echo -e "${BLUE} Для отправки в реестр используйте: ./publish_docker_image.sh${NC}"
    fi
    
else
    echo ""
    echo -e "${RED} Ошибка сборки${NC}"
    exit 1
fi
