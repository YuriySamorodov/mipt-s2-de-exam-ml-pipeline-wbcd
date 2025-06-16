#!/bin/bash

#  Скрипт для экспорта Docker-образов в файлы
# Автор: ML Pipeline Project
# Использование: ./export_docker_images.sh [версия]

set -e

# Конфигурация
IMAGE_NAME="ml-pipeline-airflow"
VERSION=${1:-"latest"}
EXPORT_DIR="docker-images"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE} Экспорт Docker-образа ${IMAGE_NAME}:${VERSION}${NC}"
echo "=================================================="

# Создание папки для экспорта
mkdir -p "${EXPORT_DIR}"

# Проверка наличия образа
if ! docker images | grep -q "${IMAGE_NAME}.*${VERSION}"; then
    echo -e "${RED} Образ ${IMAGE_NAME}:${VERSION} не найден локально${NC}"
    echo -e "${YELLOW} Сначала соберите образ: ./build_docker_image.sh${NC}"
    exit 1
fi

echo -e "${BLUE} Информация об образе:${NC}"
docker images | grep "${IMAGE_NAME}" | head -3

# Получение размера образа
IMAGE_SIZE=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "${IMAGE_NAME}" | grep "${VERSION}" | awk '{print $3}')
echo -e "${BLUE} Размер образа: ${IMAGE_SIZE}${NC}"

# Функция экспорта в разных форматах
export_image() {
    local format=$1
    local filename=$2
    local description=$3
    
    echo -e "${BLUE} ${description}...${NC}"
    
    case $format in
        "tar")
            if docker save "${IMAGE_NAME}:${VERSION}" > "${EXPORT_DIR}/${filename}"; then
                echo -e "${GREEN} Создан: ${EXPORT_DIR}/${filename}${NC}"
                ls -lh "${EXPORT_DIR}/${filename}"
            else
                echo -e "${RED} Ошибка создания ${filename}${NC}"
                return 1
            fi
            ;;
        "tar.gz")
            if docker save "${IMAGE_NAME}:${VERSION}" | gzip > "${EXPORT_DIR}/${filename}"; then
                echo -e "${GREEN} Создан: ${EXPORT_DIR}/${filename}${NC}"
                ls -lh "${EXPORT_DIR}/${filename}"
            else
                echo -e "${RED} Ошибка создания ${filename}${NC}"
                return 1
            fi
            ;;
        "tar.xz")
            if docker save "${IMAGE_NAME}:${VERSION}" | xz -9 > "${EXPORT_DIR}/${filename}"; then
                echo -e "${GREEN} Создан: ${EXPORT_DIR}/${filename}${NC}"
                ls -lh "${EXPORT_DIR}/${filename}"
            else
                echo -e "${RED} Ошибка создания ${filename}${NC}"
                return 1
            fi
            ;;
    esac
}

# Экспорт в разных форматах
echo ""
echo -e "${BLUE} Экспорт образа в файлы:${NC}"

# TAR (без сжатия) - быстро
export_image "tar" "${IMAGE_NAME}-${VERSION}.tar" "Экспорт в TAR формат"

# TAR.GZ (сжатие gzip) - хороший баланс
export_image "tar.gz" "${IMAGE_NAME}-${VERSION}.tar.gz" "Экспорт в TAR.GZ формат (сжатый)"

# TAR.XZ (максимальное сжатие) - медленно, но компактно
export_image "tar.xz" "${IMAGE_NAME}-${VERSION}.tar.xz" "Экспорт в TAR.XZ формат (максимальное сжатие)"

# Создание информационного файла
INFO_FILE="${EXPORT_DIR}/${IMAGE_NAME}-${VERSION}_info.txt"
cat > "${INFO_FILE}" << EOF
Docker Image Export Info
========================

Image Name: ${IMAGE_NAME}
Version: ${VERSION}
Export Date: $(date)
Export Directory: ${EXPORT_DIR}

Original Image Size: ${IMAGE_SIZE}

Exported Files:
$(ls -lh ${EXPORT_DIR}/${IMAGE_NAME}-${VERSION}.* 2>/dev/null || echo "No files found")

Import Commands:
================

# Импорт TAR файла
docker load < ${EXPORT_DIR}/${IMAGE_NAME}-${VERSION}.tar

# Импорт TAR.GZ файла
gunzip -c ${EXPORT_DIR}/${IMAGE_NAME}-${VERSION}.tar.gz | docker load

# Импорт TAR.XZ файла
xz -dc ${EXPORT_DIR}/${IMAGE_NAME}-${VERSION}.tar.xz | docker load

Verification:
=============
docker images ${IMAGE_NAME}:${VERSION}
docker run --rm ${IMAGE_NAME}:${VERSION} airflow version

Distribution:
=============
# Для распространения через веб
# Загрузите файлы из папки ${EXPORT_DIR}/ на файловый сервер
# Пользователи смогут скачать и импортировать образ

# Для GitHub Releases
# Загрузите .tar.gz файл в GitHub Releases
# Пользователи смогут скачать через браузер

EOF

echo -e "${GREEN} Создан информационный файл: ${INFO_FILE}${NC}"

# Создание README для папки
README_FILE="${EXPORT_DIR}/README.md"
cat > "${README_FILE}" << EOF
#  Docker Images Export

Эта папка содержит экспортированные Docker образы проекта ML Pipeline.

##  Содержимое

\`\`\`
docker-images/
 ml-pipeline-airflow-latest.tar      # Образ без сжатия (быстрый импорт)
 ml-pipeline-airflow-latest.tar.gz   # Образ со сжатием gzip (рекомендуется)
 ml-pipeline-airflow-latest.tar.xz   # Образ с максимальным сжатием
 ml-pipeline-airflow-latest_info.txt # Информация об экспорте
 README.md                           # Этот файл
\`\`\`

##  Импорт образа

### Из TAR файла (самый быстрый)
\`\`\`bash
docker load < docker-images/ml-pipeline-airflow-latest.tar
\`\`\`

### Из TAR.GZ файла (рекомендуется)
\`\`\`bash
gunzip -c docker-images/ml-pipeline-airflow-latest.tar.gz | docker load
\`\`\`

### Из TAR.XZ файла (максимальное сжатие)
\`\`\`bash
xz -dc docker-images/ml-pipeline-airflow-latest.tar.xz | docker load
\`\`\`

##  Проверка импорта

\`\`\`bash
# Проверить наличие образа
docker images ml-pipeline-airflow:latest

# Проверить работоспособность
docker run --rm ml-pipeline-airflow:latest airflow version
\`\`\`

##  Распространение

### Через веб-сервер
Загрузите файлы на ваш веб-сервер и предоставьте ссылки для скачивания.

### Через GitHub Releases
Загрузите .tar.gz файл в GitHub Releases вашего репозитория.

### Через облачные хранилища
Загрузите файлы в Google Drive, Dropbox, OneDrive и поделитесь ссылками.

##  Сравнение форматов

| Формат | Размер | Скорость импорта | Рекомендация |
|--------|--------|------------------|--------------|
| .tar | Самый большой | Самая быстрая | Локальное использование |
| .tar.gz | Средний | Быстрая | Рекомендуется для распространения |
| .tar.xz | Самый маленький | Медленная | Медленные соединения |

EOF

echo ""
echo "=================================================="
echo -e "${GREEN} Экспорт завершен успешно!${NC}"
echo ""
echo -e "${BLUE} Файлы сохранены в папке: ${EXPORT_DIR}/${NC}"
ls -lah "${EXPORT_DIR}/"

echo ""
echo -e "${BLUE} Сводка размеров:${NC}"
du -h "${EXPORT_DIR}"/${IMAGE_NAME}-${VERSION}.* 2>/dev/null | sort -h

echo ""
echo -e "${BLUE} Для импорта образа используйте команды из файла ${INFO_FILE}${NC}"
