# Руководство по публикации Docker образов

## Быстрый старт

### Автоматическая публикация (рекомендуется)
```bash
# 1. Соберите образ
./build_docker_image.sh

# 2. Опубликуйте во все реестры
./publish_docker_image.sh
```

### Ручная публикация
```bash
# Соберите образ
./build_docker_image.sh

# Войдите в реестры
docker login # Docker Hub
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin # GitHub

# Опубликуйте образ
./publish_docker_image.sh v1.0.0
```

## Поддерживаемые реестры

### 1. Docker Hub
**Основной публичный реестр**

```bash
# Регистрация: https://hub.docker.com
# Создайте репозиторий: ml-pipeline-airflow

# Публикация
docker login
docker tag ml-pipeline-airflow:latest yourusername/ml-pipeline-airflow:latest
docker push yourusername/ml-pipeline-airflow:latest
```

**Результат:** `docker pull yourusername/ml-pipeline-airflow:latest`

### 2. GitHub Container Registry
**Интеграция с GitHub**

```bash
# Создайте Personal Access Token с правами packages:write
# Settings Developer settings Personal access tokens

# Публикация
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin
docker tag ml-pipeline-airflow:latest ghcr.io/yourusername/ml-pipeline-airflow:latest
docker push ghcr.io/yourusername/ml-pipeline-airflow:latest
```

**Результат:** `docker pull ghcr.io/yourusername/ml-pipeline-airflow:latest`

## Облачные провайдеры

### AWS ECR Public
```bash
# Создайте публичный репозиторий в AWS ECR
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

# Публикация
docker tag ml-pipeline-airflow:latest public.ecr.aws/youralias/ml-pipeline-airflow:latest
docker push public.ecr.aws/youralias/ml-pipeline-airflow:latest
```

### Google Artifact Registry
```bash
# Настройте gcloud CLI
gcloud auth configure-docker

# Публикация
docker tag ml-pipeline-airflow:latest gcr.io/your-project/ml-pipeline-airflow:latest
docker push gcr.io/your-project/ml-pipeline-airflow:latest
```

## CI/CD автоматизация

### GitHub Actions
Файл уже создан: `.github/workflows/docker-publish.yml`

Образ будет автоматически собираться и публиковаться при:
- Push в main ветку
- Создании тега версии (v1.0.0)
- Pull Request

### Настройка секретов
В настройках GitHub репозитория добавьте:
- `DOCKER_USERNAME` - имя пользователя Docker Hub
- `DOCKER_PASSWORD` - пароль Docker Hub
- `GITHUB_TOKEN` - автоматически доступен

## Мониторинг и управление

### Проверка публикации
```bash
# Проверка доступности образа
docker pull yourusername/ml-pipeline-airflow:latest

# Проверка в разных реестрах
docker pull ghcr.io/yourusername/ml-pipeline-airflow:latest
```

### Управление версиями
```bash
# Публикация конкретной версии
./publish_docker_image.sh v2.1.0

# Публикация с тегом latest
./publish_docker_image.sh latest

# Проверка всех версий
docker search yourusername/ml-pipeline-airflow
```

## Чек-лист публикации

### Перед публикацией
- [ ] Образ собран и протестирован локально
- [ ] Проверена работоспособность ML pipeline
- [ ] Обновлены версии в коде
- [ ] Созданы аккаунты в реестрах

### Процесс публикации
- [ ] Аутентификация в реестрах
- [ ] Запуск скрипта публикации
- [ ] Проверка успешной загрузки
- [ ] Тестирование скачивания

### После публикации
- [ ] Обновлен README.md с новыми ссылками
- [ ] Обновлена документация
- [ ] Уведомлены пользователи
- [ ] Удалены старые версии (по необходимости)

## Troubleshooting

### Ошибка аутентификации
```bash
# Docker Hub
docker logout
docker login

# GitHub Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin
```

### Медленная загрузка
```bash
# Используйте параллельную загрузку
docker push --parallel yourusername/ml-pipeline-airflow:latest

# Проверьте размер образа
docker images ml-pipeline-airflow:latest
```

### Превышение лимитов
- Docker Hub: 1 GB для бесплатных аккаунтов
- GitHub Registry: Бесплатно для публичных репозиториев

## Быстрые команды

```bash
# Полный цикл публикации
./build_docker_image.sh && ./publish_docker_image.sh

# Публикация конкретной версии
./publish_docker_image.sh v2.0.0

# Проверка всех образов
docker images | grep ml-pipeline-airflow

# Очистка локальных образов
docker rmi $(docker images ml-pipeline-airflow:* -q)
```

## Полезные ссылки

- [Docker Hub](https://hub.docker.com)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [AWS ECR Public](https://gallery.ecr.aws)
- [Google Artifact Registry](https://cloud.google.com/artifact-registry)
