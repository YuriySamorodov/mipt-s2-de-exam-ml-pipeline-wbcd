# Airflow Configuration Guide

## Три варианта запуска ML Pipeline Airflow

### 1. SQLite + SequentialExecutor (порт 8081)
**Рекомендуется для:** разработки и тестирования
- **База данных:** SQLite (локальный файл)
- **Executor:** SequentialExecutor (выполняет задачи последовательно)
- **Порт:** 8081
- **Команда:** `make airflow-sqlite` или `./scripts/airflow/start_airflow_sqlite_8081.sh`
- **Web UI:** http://localhost:8081

### 2. PostgreSQL + LocalExecutor (порт 8082) 
**Рекомендуется для:** локального продакшена
- **База данных:** PostgreSQL (локальная установка)
- **Executor:** LocalExecutor (может выполнять задачи параллельно)
- **Порт:** 8082
- **Команда:** `make airflow-postgres` или `./scripts/airflow/start_airflow_postgres_8082.sh`
- **Web UI:** http://localhost:8082
- **Требования:** PostgreSQL должен быть запущен локально

### 3. Docker + PostgreSQL + LocalExecutor (порт 8083)
**Рекомендуется для:** продакшена и изоляции
- **База данных:** PostgreSQL (в Docker контейнере)
- **Executor:** LocalExecutor (параллельное выполнение)
- **Порт:** 8083 (внешний), 8082 (внутренний в контейнере)
- **Команда:** `make airflow-docker` или `./scripts/airflow/start_airflow_docker_8083.sh`
- **Web UI:** http://localhost:8083
- **Требования:** Docker и docker-compose

## Краткий справочник команд

```bash
# Показать все варианты
make airflow-guide
./airflow_start_guide.sh

# Запуск конкретного варианта
make airflow-sqlite # SQLite + SequentialExecutor (8081)
make airflow-postgres # PostgreSQL + LocalExecutor (8082) 
make airflow-docker # Docker + PostgreSQL + LocalExecutor (8083)

# Остановка
make airflow-stop # Для SQLite и PostgreSQL
./scripts/airflow/stop_airflow_docker.sh # Для Docker
```

## Доступ к Web UI

**Для всех вариантов:**
- **Логин:** admin
- **Пароль:** admin

## Технические различия

| Вариант | База данных | Executor | Порт | Параллельность | Использование |
|---------|------------|----------|------|----------------|---------------|
| SQLite | SQLite | SequentialExecutor | 8081 | Нет | Разработка, тесты |
| PostgreSQL | PostgreSQL | LocalExecutor | 8082 | Да | Локальный продакшн |
| Docker | PostgreSQL | LocalExecutor | 8083 (8082) | Да | Продакшн, изоляция |

## Структура файлов

```
scripts/airflow/
├── start_airflow_sqlite_8081.sh # SQLite вариант
├── start_airflow_postgres_8082.sh # PostgreSQL вариант 
├── start_airflow_docker_8083.sh # Docker вариант
└── stop_airflow_*.sh # Скрипты остановки
```

## Рекомендации

- **Для начала работы:** используйте SQLite вариант (порт 8081)
- **Для разработки с параллельностью:** PostgreSQL вариант (порт 8082)
- **Для продакшена:** Docker вариант (порт 8083)
