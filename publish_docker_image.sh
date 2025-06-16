#!/bin/bash

#  Скрипт для публикации Docker-образа в несколько реестров
# Автор: ML Pipeline Project
# Использование: ./publish_docker_image.sh [версия] [--export-files] [--multiplatform]

set -e

# Конфигурация
IMAGE_NAME="ml-pipeline-airflow"
VERSION=${1:-"latest"}
EXPORT_FILES=false
MULTIPLATFORM=false
PLATFORMS="linux/amd64,linux/arm64"

# Проверка аргументов
for arg in "$@"; do
    case $arg in
        --export-files)
            EXPORT_FILES=true
            shift
            ;;
        --multiplatform)
            MULTIPLATFORM=true
            shift
            ;;
        --platforms=*)
            PLATFORMS="${arg#*=}"
            shift
            ;;
    esac
done

REGISTRIES=(
    "docker.io"
    "ghcr.io"
)

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE} Публикация Docker-образа ${IMAGE_NAME}:${VERSION}${NC}"
if [ "$MULTIPLATFORM" = true ]; then
    echo -e "${BLUE} Мультиплатформенная сборка: ${PLATFORMS}${NC}"
fi
echo "=================================================="

# Проверка наличия образа (только для локальной публикации)
if [ "$MULTIPLATFORM" = false ]; then
    if ! docker images | grep -q "${IMAGE_NAME}.*${VERSION}"; then
        echo -e "${RED} Образ ${IMAGE_NAME}:${VERSION} не найден локально${NC}"
        echo -e "${YELLOW} Сначала соберите образ: ./build_docker_image.sh${NC}"
        exit 1
    fi
fi

# Функция для публикации в реестр
publish_to_registry() {
    local registry=$1
    local username=$2
    
    echo -e "${BLUE} Публикация в ${registry}...${NC}"
    
    # Тегирование образа
    local full_tag="${registry}/${username}/${IMAGE_NAME}:${VERSION}"
    
    if [ "$MULTIPLATFORM" = true ]; then
        # Мультиплатформенная сборка и публикация
        echo -e "${BLUE} Мультиплатформенная сборка для ${registry}${NC}"
        
        # Создание тегов для buildx
        local buildx_tags="--tag ${full_tag}"
        if [ "${VERSION}" != "latest" ]; then
            local latest_tag="${registry}/${username}/${IMAGE_NAME}:latest"
            buildx_tags="$buildx_tags --tag ${latest_tag}"
        fi
        
        # Сборка и публикация через buildx
        if docker buildx build \
            --platform "${PLATFORMS}" \
            --file Dockerfile.local \
            $buildx_tags \
            --push .; then
            echo -e "${GREEN} Успешно опубликовано: ${full_tag}${NC}"
            if [ "${VERSION}" != "latest" ]; then
                echo -e "${GREEN} Успешно опубликовано: ${latest_tag}${NC}"
            fi
        else
            echo -e "${RED} Ошибка мультиплатформенной публикации в ${registry}${NC}"
            return 1
        fi
    else
        # Обычная публикация локального образа
        docker tag "${IMAGE_NAME}:${VERSION}" "${full_tag}"
        
        # Публикация
        if docker push "${full_tag}"; then
            echo -e "${GREEN} Успешно опубликовано: ${full_tag}${NC}"
            
            # Если версия не latest, также публикуем latest
            if [ "${VERSION}" != "latest" ]; then
                local latest_tag="${registry}/${username}/${IMAGE_NAME}:latest"
                docker tag "${IMAGE_NAME}:${VERSION}" "${latest_tag}"
                docker push "${latest_tag}"
                echo -e "${GREEN} Успешно опубликовано: ${latest_tag}${NC}"
            fi
        else
            echo -e "${RED} Ошибка публикации в ${registry}${NC}"
            return 1
        fi
    fi
}

# Получение имени пользователя для разных реестров
get_username() {
    local registry=$1
    
    case $registry in
        "docker.io")
            echo "${DOCKER_USERNAME:-$(whoami)}"
            ;;
        "ghcr.io")
            echo "${GITHUB_USERNAME:-$(whoami)}"
            ;;
        *)
            echo "$(whoami)"
            ;;
    esac
}

# Проверка аутентификации
check_auth() {
    local registry=$1
    
    echo -e "${YELLOW} Проверка аутентификации для ${registry}...${NC}"
    
    case $registry in
        "docker.io")
            if ! docker info | grep -q "Username:"; then
                echo -e "${YELLOW}  Не авторизованы в Docker Hub. Выполните: docker login${NC}"
                return 1
            fi
            ;;
        "ghcr.io")
            if ! docker info 2>/dev/null | grep -q "ghcr.io"; then
                echo -e "${YELLOW}  Не авторизованы в GHCR. Выполните: echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin${NC}"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Основной процесс публикации
echo -e "${BLUE} Информация об образе:${NC}"
if [ "$MULTIPLATFORM" = false ]; then
    docker images | grep "${IMAGE_NAME}" | head -5
fi

echo ""
echo -e "${BLUE} Целевые реестры:${NC}"
for registry in "${REGISTRIES[@]}"; do
    username=$(get_username "$registry")
    echo "  • ${registry}/${username}/${IMAGE_NAME}:${VERSION}"
done

if [ "$MULTIPLATFORM" = true ]; then
    echo ""
    echo -e "${BLUE} Поддерживаемые платформы: ${PLATFORMS}${NC}"
fi

echo ""
read -p "Продолжить публикацию? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW} Публикация отменена${NC}"
    exit 0
fi

# Публикация в каждый реестр
success_count=0
total_count=${#REGISTRIES[@]}

for registry in "${REGISTRIES[@]}"; do
    username=$(get_username "$registry")
    
    echo ""
    echo -e "${BLUE} Обработка ${registry}...${NC}"
    
    if check_auth "$registry"; then
        if publish_to_registry "$registry" "$username"; then
            ((success_count++))
        fi
    else
        echo -e "${YELLOW}⏭  Пропуск ${registry} - требуется аутентификация${NC}"
    fi
done

# Итоговый отчет
echo ""
echo "=================================================="
echo -e "${BLUE} Результаты публикации:${NC}"
echo -e "${GREEN} Успешно: ${success_count}/${total_count}${NC}"

if [ $success_count -gt 0 ]; then
    echo ""
    echo -e "${GREEN} Образ успешно опубликован!${NC}"
    echo -e "${BLUE} Пользователи могут скачать образ командами:${NC}"
    
    for registry in "${REGISTRIES[@]}"; do
        username=$(get_username "$registry")
        echo "docker pull ${registry}/${username}/${IMAGE_NAME}:${VERSION}"
    done
    
    echo ""
    echo -e "${BLUE} Обновите README.md с актуальными ссылками на образы${NC}"
    
    # Экспорт в файлы (если запрошено)
    if [ "$EXPORT_FILES" = true ]; then
        echo ""
        echo -e "${BLUE} Экспорт образа в файлы...${NC}"
        if ./export_docker_images.sh "$VERSION"; then
            echo -e "${GREEN} Образы экспортированы в папку docker-images/${NC}"
        else
            echo -e "${YELLOW}  Ошибка экспорта файлов (не критично)${NC}"
        fi
    fi
else
    echo -e "${RED} Не удалось опубликовать образ ни в одном реестре${NC}"
    exit 1
fi
