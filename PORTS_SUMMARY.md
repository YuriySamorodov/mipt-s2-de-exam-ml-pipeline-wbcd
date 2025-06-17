# Портовая схема ML Pipeline

## Итоговая конфигурация портов

После исправлений все три варианта запуска используют правильные порты:

### 1. SQLite + SequentialExecutor
- **Порт:** 8081
- **URL:** http://localhost:8081
- **Конфигурация:** `AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8081`
- **Запуск:** `make airflow-sqlite` или `./scripts/airflow/start_airflow_sqlite_8081.sh`

### 2. PostgreSQL + LocalExecutor (локальный)
- **Порт:** 8082
- **URL:** http://localhost:8082
- **Конфигурация:** `AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8082`
- **Запуск:** `make airflow-postgres` или `./scripts/airflow/start_airflow_postgres_8082.sh`

### 3. Docker + PostgreSQL + LocalExecutor
- **Внешний порт:** 8083
- **Внутренний порт:** 8082
- **URL:** http://localhost:8083
- **Конфигурация:** 
- `AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8082` (внутри контейнера)
- `ports: "8083:8082"` (маппинг портов)
- `command: webserver --port 8082`
- **Запуск:** `make airflow-docker` или `./scripts/airflow/start_airflow_docker_8083.sh`

## Исправленные файлы

### Docker конфигурация:
- `docker/docker-compose.yml` - основной файл
- `docker/docker-compose-original.yml` 
- `docker/docker-compose-optimized.yml`
- `docker/docker-compose.single-repo.yml`
- `docker/Dockerfile.full`
- `docker/Dockerfile.local`

### Документация:
- `docs/AIRFLOW_VARIANTS.md` - обновлена таблица портов

## Проверка конфигурации

```bash
# Проверить docker-compose конфигурацию
docker-compose -f docker/docker-compose.yml config | grep -E "WEB_SERVER_PORT|ports|8082|8083"

# Запустить проверку портов
./scripts/airflow/check_ports.sh # если есть такой скрипт
```

## Принцип наименования

- **SQLite:** порт 8081 (базовый)
- **PostgreSQL:** порт 8082 (базовый + 1) 
- **Docker:** внешний 8083 (базовый + 2), внутренний 8082 (как PostgreSQL)

Логика: Docker использует тот же внутренний порт, что и локальный PostgreSQL (8082), но маппирует его на внешний порт 8083 для избежания конфликтов.
