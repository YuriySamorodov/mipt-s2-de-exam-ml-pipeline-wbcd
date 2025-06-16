# Руководство по скачиванию Docker образа

## Быстрый старт

### Автоматическое скачивание (рекомендуется)
```bash
git clone <repository-url>
cd ml-pipeline-project
docker-compose up -d # Образ скачается автоматически
```

### Ручное скачивание
```bash
# Основная команда
docker pull ml-pipeline-airflow:latest

# Затем запуск
docker-compose up -d
```

## Источники образа

### Docker Hub (публичный реестр)
```bash
# Основной репозиторий
docker pull ml-pipeline-airflow:latest

# С указанием полного пути
docker pull docker.io/ml-pipeline-airflow:latest

# Конкретная версия
docker pull ml-pipeline-airflow:v2.0.0
docker pull ml-pipeline-airflow:stable
```

**URL:** https://hub.docker.com/r/ml-pipeline-airflow

### GitHub Container Registry
```bash
# Основная команда
docker pull ghcr.io/username/ml-pipeline-airflow:latest

# С аутентификацией
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/username/ml-pipeline-airflow:latest
```

**URL:** https://github.com/username/ml-pipeline-project/pkgs/container/ml-pipeline-airflow

### Корпоративный реестр
```bash
# Внутренний реестр компании
docker login registry.company.com
docker pull registry.company.com/ml-pipeline-airflow:latest
```

## Альтернативные способы получения

### 1. Локальная сборка
```bash
# Сборка образа самостоятельно
git clone <repository-url>
cd ml-pipeline-project
./build_docker_image.sh
```

### 2. Экспорт/Импорт образа
```bash
# Экспорт образа в файл (от другого пользователя)
docker save ml-pipeline-airflow:latest > ml-pipeline-airflow.tar

# Импорт образа из файла
docker load < ml-pipeline-airflow.tar
```

### 3. Облачные artifacts
```bash
# Скачивание из CI/CD artifacts
curl -O https://artifacts.company.com/ml-pipeline-airflow-latest.tar
docker load < ml-pipeline-airflow-latest.tar

# Из GitHub Releases
curl -L https://github.com/username/ml-pipeline-project/releases/download/v2.0.0/ml-pipeline-airflow.tar \
 | docker load
```

## Аутентификация

### Docker Hub
```bash
# Регистрация и вход
docker login

# Ввести username и password
```

### GitHub Container Registry
```bash
# Создание Personal Access Token с правами read:packages
# https://github.com/settings/tokens

# Вход
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### Корпоративный реестр
```bash
# Вход в приватный реестр
docker login registry.company.com

# С токеном
echo $REGISTRY_TOKEN | docker login registry.company.com -u USERNAME --password-stdin
```

## Проверка скачивания

### Проверка наличия образа
```bash
# Список всех образов
docker images

# Поиск конкретного образа
docker images ml-pipeline-airflow

# Ожидаемый результат:
# REPOSITORY TAG IMAGE ID CREATED SIZE
# ml-pipeline-airflow latest 667511c0b76d 2 hours ago 2.84GB
```

### Детальная информация
```bash
# Информация об образе
docker inspect ml-pipeline-airflow:latest

# История слоев
docker history ml-pipeline-airflow:latest

# Проверка содержимого
docker run --rm ml-pipeline-airflow:latest ls -la /opt/airflow/
```

### Health Check
```bash
# Быстрая проверка работоспособности
docker run --rm ml-pipeline-airflow:latest python --version
docker run --rm ml-pipeline-airflow:latest airflow version

# Проверка установленных пакетов
docker run --rm ml-pipeline-airflow:latest pip list | grep -E "(pandas|scikit|airflow)"
```

## Troubleshooting

### Образ не найден
```bash
# Проблема: ERROR: pull access denied
# Решение 1: Проверить правописание имени
docker pull ml-pipeline-airflow:latest # Правильно
docker pull ml-pipeline-aiflow:latest # Ошибка в имени

# Решение 2: Попробовать альтернативный реестр
docker pull ghcr.io/username/ml-pipeline-airflow:latest

# Решение 3: Проверить доступные теги
docker search ml-pipeline-airflow
```

### Медленное скачивание
```bash
# Использование зеркала Docker Hub
docker pull --disable-content-trust docker.mirrors.ustc.edu.cn/ml-pipeline-airflow:latest

# Параллельное скачивание слоев
docker pull --parallel ml-pipeline-airflow:latest

# Проверка скорости соединения
docker info | grep -A5 "Registry Mirrors"
```

### Проблемы с аутентификацией
```bash
# Проблема: unauthorized
# Решение: Перелогиниться
docker logout
docker login

# Проверить текущего пользователя
docker info | grep Username

# Для GitHub Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### Недостаточно места
```bash
# Проверка места на диске
df -h

# Очистка неиспользуемых образов
docker image prune -a

# Удаление старых контейнеров
docker container prune

# Полная очистка Docker
docker system prune -a --volumes
```

## Обновление образа

### Проверка обновлений
```bash
# Принудительное скачивание новой версии
docker pull ml-pipeline-airflow:latest

# Проверка изменений
docker images ml-pipeline-airflow

# Сравнение с предыдущей версией
docker diff <old_container_id> <new_container_id>
```

### Обновление running контейнеров
```bash
# Остановка текущих контейнеров
docker-compose down

# Скачивание обновлений
docker-compose pull

# Запуск с новыми образами
docker-compose up -d

# Или одной командой
docker-compose pull && docker-compose up -d
```

## Поддержка

**Если образ недоступен:**
1. Свяжитесь с администратором проекта
2. Соберите образ локально: `./build_docker_image.sh`
3. Проверьте issues в репозитории GitHub

**Альтернативные источники:**
- GitHub Releases: https://github.com/username/ml-pipeline-project/releases
- Docker Hub: https://hub.docker.com/r/ml-pipeline-airflow
- Корпоративный реестр: registry.company.com

---

** Актуально на:** Июнь 2025
** Версия образа:** latest (2.84GB)
** Статус:** Production Ready
