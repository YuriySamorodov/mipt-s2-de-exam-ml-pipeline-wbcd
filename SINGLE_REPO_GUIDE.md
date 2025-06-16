# Single Repository Docker Hub Setup

> **Обновлено**: Исправлены проблемы с передачей аргументов между скриптами.
> Теперь `setup_single_repo.sh` корректно передает версию и username в `build_and_publish_repo.sh`.

## Концепция

Этот подход размещает два отдельных образа (PostgreSQL и Airflow) в одном репозитории Docker Hub с разными тегами:

```
yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest # Apache Airflow + ML Pipeline
yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest # PostgreSQL для Airflow
```

> **Готовые образы уже доступны**: Вы можете сразу использовать готовые образы или собрать свои собственные.

## Быстрый старт

### Вариант 1: Использование готовых образов (рекомендуется)
```bash
# 1. Клонируйте проект
git clone <repository-url>
cd ml-pipeline-project

# 2. Запустите с готовыми образами
docker-compose -f docker-compose.single-repo.yml up -d

# Образы скачаются автоматически:
# - yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest
# - yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest
```

### Вариант 2: Сборка собственных образов
```bash
# Скопируйте переменные окружения
cp .env.example .env

# Отредактируйте .env файл
nano .env
# Установите DOCKER_USERNAME=ваш_docker_hub_username

# Локальная сборка (тестирование)
./build_and_publish_repo.sh

# Сборка и публикация в Docker Hub
./build_and_publish_repo.sh latest --push

# С кастомным username
./build_and_publish_repo.sh --username=myusername --push
```

### 3. Запуск
```bash
# Используя docker-compose для single-repo
docker-compose -f docker-compose.single-repo.yml up -d

# Или с переменными окружения
DOCKER_USERNAME=myusername VERSION=v1.0.0 docker-compose -f docker-compose.single-repo.yml up -d
```

## Структура репозитория на Docker Hub

```
yourusername/ml-pipeline/
 airflow-latest # Apache Airflow образ
 airflow-v1.0.0 # Версионированный Airflow
 postgres-latest # PostgreSQL образ
 postgres-v1.0.0 # Версионированный PostgreSQL
 README.md # Описание репозитория
```

## Файлы проекта

### Dockerfile'ы
- `Dockerfile.local` - для Airflow образа
- `Dockerfile.postgres` - для PostgreSQL образа

### Docker Compose
- `docker-compose.single-repo.yml` - для single-repo подхода
- `docker-compose.yml` - оригинальный (разные репозитории)

### Скрипты
- `build_and_publish_repo.sh` - сборка и публикация обоих образов

## Преимущества single-repo подхода

| Преимущество | Описание |
|--------------|----------|
| **Связанность** | Оба образа в одном месте |
| **Простота** | Один репозиторий для управления |
| **Версионирование** | Синхронные версии образов |
| **Документация** | Единое место для описания |

## Команды для пользователей

### Скачивание образов
```bash
# Оба образа одной командой
docker pull yourusername/ml-pipeline:airflow-latest
docker pull yourusername/ml-pipeline:postgres-latest

# Конкретная версия
docker pull yourusername/ml-pipeline:airflow-v1.0.0
docker pull yourusername/ml-pipeline:postgres-v1.0.0
```

### Запуск системы
```bash
# Создайте .env файл
echo "DOCKER_USERNAME=yourusername" > .env
echo "VERSION=latest" >> .env

# Запуск
docker-compose -f docker-compose.single-repo.yml up -d

# Проверка
docker-compose -f docker-compose.single-repo.yml ps
curl http://localhost:8080
```

### Создание собственного docker-compose.yml
```yaml
version: '3.8'
services:
 postgres:
 image: yourusername/ml-pipeline:postgres-latest
 environment:
 POSTGRES_DB: airflow
 POSTGRES_USER: airflow
 POSTGRES_PASSWORD: airflow
 volumes:
 - postgres_data:/var/lib/postgresql/data
 ports:
 - "5432:5432"

 airflow:
 image: yourusername/ml-pipeline:airflow-latest
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
```

## Развертывание в разных средах

### Development
```bash
DOCKER_USERNAME=myusername VERSION=dev docker-compose -f docker-compose.single-repo.yml up -d
```

### Staging
```bash
DOCKER_USERNAME=myusername VERSION=staging docker-compose -f docker-compose.single-repo.yml up -d
```

### Production
```bash
DOCKER_USERNAME=myusername VERSION=v1.0.0 docker-compose -f docker-compose.single-repo.yml up -d
```

## Сравнение подходов

| Критерий | Single Repo | Separate Repos |
|----------|-------------|----------------|
| **Управление** | Проще | Сложнее |
| **Версионирование** | Синхронное | Может рассинхронизироваться |
| **Размер репозитория** | Больше | Меньше |
| **Гибкость** | Меньше | Больше |
| **CI/CD** | Проще настроить | Нужно два pipeline |

## Публикация в Docker Hub

### Подготовка
1. Создайте аккаунт на [Docker Hub](https://hub.docker.com)
2. Создайте репозиторий `ml-pipeline`
3. Выполните `docker login`

### Автоматическая публикация
```bash
# Установите ваш username
export DOCKER_USERNAME=yourusername

# Соберите и опубликуйте
./build_and_publish_repo.sh latest --push
```

### Результат
После публикации пользователи смогут:
```bash
docker pull yourusername/ml-pipeline:airflow-latest
docker pull yourusername/ml-pipeline:postgres-latest
```

## Документация для Docker Hub

Добавьте в описание репозитория на Docker Hub:

```markdown
# ML Pipeline для диагностики рака молочной железы

Готовый к продакшену ML pipeline на Apache Airflow с PostgreSQL.

## Образы
- `ml-pipeline:airflow-latest` - Apache Airflow + ML Pipeline
- `ml-pipeline:postgres-latest` - PostgreSQL база данных

## Быстрый старт
```bash
docker-compose up -d
```

Airflow UI: http://localhost:8080 (admin/admin)
```

## Статус решения проблем

### Исправлены ошибки зависимостей ( Декабрь 2024)
- **Проблема**: Ошибки сборки Docker из-за конфликтов версий Python-зависимостей
- **Решение**:
 - Исправлен `requirements.txt`: удален sqlite3, понижены версии SQLAlchemy, pydantic, numpy, matplotlib
 - Версии приведены в соответствие с Apache Airflow 2.8.1
 - Проведено успешное тестирование сборки с полным набором ML-зависимостей
- **Результат**: Образы собираются успешно за ~2.5 минуты

### Исправлена передача аргументов ( Декабрь 2024)
- **Проблема**: Некорректная передача username и version между скриптами
- **Решение**: Исправлен парсинг аргументов в `build_and_publish_repo.sh` и `setup_single_repo.sh`
- **Результат**: Корректное создание тегов вида `airflow-vX.Y.Z` и `postgres-vX.Y.Z`

Теперь у вас есть полная система для публикации двух образов в одном Docker Hub репозитории!
