# Быстрая публикация Docker образа

## 3 простых шага

### 1. Подготовка
```bash
# Соберите образ
./build_docker_image.sh

# Проверьте образ
docker images ml-pipeline-airflow
```

### 2. Аутентификация
```bash
# Docker Hub (основной)
docker login

# GitHub Registry (опционально)
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin
```

### 3. Публикация
```bash
# Автоматическая публикация во все реестры
./publish_docker_image.sh

# Или публикация конкретной версии
./publish_docker_image.sh v1.0.0
```

## Результат

После публикации пользователи смогут скачать образ:

```bash
# Из Docker Hub
docker pull yourusername/ml-pipeline-airflow:latest

# Из GitHub Registry
docker pull ghcr.io/yourusername/ml-pipeline-airflow:latest
```

## Подробная документация

См. [DOCKER_IMAGE_PUBLISHING_GUIDE.md](DOCKER_IMAGE_PUBLISHING_GUIDE.md)
