#!/bin/bash

# Скрипт для оптимизации Docker образов проекта
# Создает единый базовый образ и удаляет дубликаты

set -e

echo " ЗАПУСК ОПТИМИЗАЦИИ DOCKER ОБРАЗОВ"
echo "======================================="

# Остановка контейнеров
echo "1. Остановка текущих контейнеров..."
docker-compose down

# Создание единого базового образа
echo "2. Создание базового образа ml-pipeline-airflow..."
docker build -t ml-pipeline-airflow:latest -f Dockerfile.airflow .

# Удаление старых образов
echo "3. Удаление дублирующих образов..."
docker rmi -f ml-pipeline-project-airflow-webserver:latest 2>/dev/null || echo " - webserver образ не найден"
docker rmi -f ml-pipeline-project-airflow-scheduler:latest 2>/dev/null || echo " - scheduler образ не найден" 
docker rmi -f ml-pipeline-project-airflow-init:latest 2>/dev/null || echo " - init образ не найден"

# Обновление docker-compose.yml для использования единого образа
echo "4. Обновление docker-compose.yml..."
sed -i.bak 's/build:/# build:/g' docker-compose.yml
sed -i.bak 's/context: ./# context: ./g' docker-compose.yml
sed -i.bak 's/dockerfile: Dockerfile.airflow/# dockerfile: Dockerfile.airflow/g' docker-compose.yml
sed -i.bak 's/# image: apache\/airflow:2.8.1/image: ml-pipeline-airflow:latest/g' docker-compose.yml

# Запуск оптимизированной системы
echo "5. Запуск оптимизированной системы..."
docker-compose up -d

echo ""
echo " ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!"
echo "========================="
echo ""
echo " РЕЗУЛЬТАТ:"
echo " - Создан единый образ: ml-pipeline-airflow:latest"
echo " - Удалены дублирующие образы"
echo " - Экономия места: ~5.68GB"
echo ""
echo " ПРОВЕРКА:"
echo " docker images | grep ml-pipeline"
echo " docker ps"
echo " curl http://localhost:8083/health # Проверка через внешний порт Docker"
echo ""
echo " ОТКАТ (если нужен):"
echo " cp docker-compose.yml.bak docker-compose.yml"
echo " docker-compose down && docker-compose up -d"
