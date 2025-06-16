# Готовые Docker образы

> **Все образы готовы к использованию!** Не требуется сборка - просто скачайте и запускайте.

## Мгновенный запуск

```bash
# 1. Клонируйте проект
git clone <repository-url>
cd ml-pipeline-project

# 2. Запустите с готовыми образами
docker-compose up -d

# Готово! Система запустится автоматически
```

## Доступные образы

### Airflow + ML Pipeline
- **Docker Hub**: https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline/tags?name=airflow
- **Тег**: `yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest`
- **Размер**: ~2.8GB
- **Содержит**:
 - Apache Airflow 2.8.1
 - Python ML библиотеки (scikit-learn, pandas, matplotlib)
 - Готовый ML pipeline для диагностики рака молочной железы
 - Оптимизированная конфигурация

### PostgreSQL
- **Docker Hub**: https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline/tags?name=postgres
- **Тег**: `yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest`
- **Размер**: ~400MB
- **Содержит**:
 - PostgreSQL 13
 - Оптимизированная конфигурация для Airflow
 - Инициализационные скрипты

## Команды скачивания

```bash
# Скачать оба образа
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest

# Или позволить docker-compose скачать автоматически
docker-compose pull
```

## Проверка образов

```bash
# Проверить доступные образы
docker images | grep yuriysamorodov

# Получить информацию об образе
docker inspect yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest

# Проверить историю слоев
docker history yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest
```

## Альтернативные варианты запуска

### 1⃣ Single-repo версия
```bash
# Использует переменные окружения для версий
docker-compose -f docker-compose.single-repo.yml up -d
```

### 2⃣ Локальная разработка
```bash
# Без Docker, только для разработки
./start_airflow_sqlite.sh
```

### 3⃣ Локальная сборка (если нужны изменения)
```bash
# Соберите образы самостоятельно
./build_docker_image.sh
docker-compose up -d
```

## Статистика образов

| Образ | Размер | Слои | Последнее обновление |
|-------|--------|------|---------------------|
| airflow-latest | ~2.8GB | 15 | 2025-06-16 |
| postgres-latest | ~400MB | 8 | 2025-06-16 |

## Настройка для своих нужд

Если вам нужно изменить образы:

1. **Форкните репозиторий**
2. **Измените Dockerfile.local и docker/postgresql.conf**
3. **Соберите свои образы**:
 ```bash
 ./setup_single_repo.sh
 # Следуйте инструкциям для ввода своего Docker Hub username
 ```

## Поддержка

- **Документация**: См. [README.md](README.md)
- **Проблемы**: Создайте issue в репозитории
- **Single-repo guide**: [SINGLE_REPO_GUIDE.md](SINGLE_REPO_GUIDE.md)

---

> **Совет**: Для production использования рекомендуется создать свои собственные образы с необходимыми настройками безопасности и конфигурациями.
