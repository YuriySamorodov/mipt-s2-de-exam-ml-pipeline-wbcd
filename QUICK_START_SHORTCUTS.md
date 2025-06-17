# Quick Start Scripts

Быстрый запуск различных конфигураций Airflow из корня проекта.

## Ярлыки в корне проекта:

### Скрипты-обертки (рекомендуется):
```bash
./start-sqlite.sh # SQLite + SequentialExecutor (порт 8081)
./start-postgres.sh # PostgreSQL + LocalExecutor (порт 8082) 
./start-docker.sh # Docker + PostgreSQL + LocalExecutor (порт 8083)
```

### Символические ссылки:
```bash
./airflow-sqlite # Symlink scripts/airflow/start_airflow_sqlite_8081.sh
./airflow-postgres # Symlink scripts/airflow/start_airflow_postgres_8082.sh
./airflow-docker # Symlink scripts/airflow/start_airflow_docker_8083.sh
```

### Make команды (также доступны):
```bash
make airflow-sqlite
make airflow-postgres
make airflow-docker
make airflow-guide
```

## Рекомендации:

**Для разработки:** используйте скрипты-обертки (`start-*.sh`)
- Кроссплатформенность
- Понятные имена файлов
- Встроенные описания

**Для автоматизации:** используйте make команды
- Стандартизация
- Интеграция с CI/CD
- Единая точка входа

**Для быстрого доступа:** используйте symlinks
- Минимальный overhead
- Прямые ссылки на скрипты
