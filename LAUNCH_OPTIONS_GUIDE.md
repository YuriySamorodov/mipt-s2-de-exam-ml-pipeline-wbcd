# Три варианта запуска ML Pipeline

## Быстрый выбор варианта

### Вариант 1: Локальная разработка
**Для кого:** Разработчики, студенты, быстрое тестирование
**Что нужно:** Только Python 3.8+

```bash
git clone <repository-url>
cd ml-pipeline-project
./start_airflow_sqlite.sh
```

### Вариант 2: Готовый образ (рекомендуется)
**Для кого:** Быстрое тестирование, демо, обучение
**Что нужно:** Docker + Docker Compose

```bash
git clone <repository-url>
cd ml-pipeline-project

# Автоматическое скачивание при запуске
docker-compose up -d

# Или предварительное скачивание
docker pull ml-pipeline-airflow:latest
docker-compose up -d
```

** Источники образа:**
- **Docker Hub**: `docker pull ml-pipeline-airflow:latest`
- **GitHub Registry**: `docker pull ghcr.io/username/ml-pipeline-airflow:latest`
- **Private Registry**: Для корпоративного использования

### Вариант 3: Локальная сборка
**Для кого:** Production deployment, кастомизация, CI/CD
**Что нужно:** Docker + Docker Compose

```bash
git clone <repository-url>
cd ml-pipeline-project
./build_docker_image.sh
docker-compose up -d
```

## Детальное сравнение

| Критерий | Локальный | Готовый образ | Локальная сборка |
|----------|-----------|---------------|------------------|
| Скорость запуска | 30 сек | 2-3 мин | 10-15 мин |
| Размер | 500MB | 2.84GB | 2.84GB |
| Сложность | Простая | Простая | Средняя |
| Производительность | Последовательно | Параллельно | Параллельно |
| Отладка | Легко | Сложнее | Сложнее |
| Кастомизация | Легко | Невозможно | Полная |
| Зависимости | Python | Docker | Docker |

## Когда использовать каждый вариант

### Локальный (SQLite + SequentialExecutor)
- **Разработка** нового функционала
- **Отладка** проблем в коде
- **Быстрые тесты** изменений
- **Обучение** работе с Airflow
- Не подходит для production

### Готовый образ (PostgreSQL + LocalExecutor)
- **Быстрая демонстрация** проекта
- **Первое знакомство** с системой
- **Тестирование функционала** без сборки
- **Обучение** на готовом примере
- Нет возможности изменить код

### Локальная сборка (PostgreSQL + LocalExecutor)
- **Production развертывание**
- **Кастомизация** под потребности
- **CI/CD интеграция**
- **Командная разработка**
- Требует времени на сборку

## Доступ к системе (все варианты)
- **URL:** http://localhost:8080
- **Логин:** `admin`
- **Пароль:** `admin`

## Созданные файлы

### Локальный запуск:
- `start_airflow_sqlite.sh` - Запуск SQLite режима
- `stop_airflow_sqlite.sh` - Остановка SQLite режима

### Docker варианты:
- `build_docker_image.sh` - Сборка образа локально
- `Dockerfile.local` - Dockerfile для локальной сборки
- `start_airflow_postgresql.sh` - Запуск PostgreSQL режима
- `stop_airflow_postgresql.sh` - Остановка PostgreSQL режима
- `docker-compose.yml` - Конфигурация для готового образа

## Выбор варианта: Быстрая шпаргалка

```bash
# Я хочу быстро посмотреть, что это за проект
docker-compose up -d # Готовый образ

# Я хочу разработать новую функцию
./start_airflow_sqlite.sh # Локальный

# Я хочу развернуть в production
./build_docker_image.sh && docker-compose up -d # Сборка
```
