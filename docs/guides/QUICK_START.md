# БЫСТРЫЙ ЗАПУСК AIRFLOW - ИНСТРУКЦИЯ

## Краткая инструкция по использованию системы

### Подготовка среды
```bash
# 1. Переходим в директорию проекта
cd ml-pipeline-project

# 2. Активируем виртуальное окружение (создается автоматически при первом запуске)
source venv/bin/activate
```

### Выбор режима развертывания

#### Вариант 1: SQLite (простой, для разработки)
```bash
# Генерируем конфигурацию
python setup_airflow_config.py

# Запускаем Airflow
./start_airflow_sqlite_8081.sh

# Веб-интерфейс: http://localhost:8081
```

#### Вариант 2: PostgreSQL (продакшн-готовый)
```bash
# Запускаем PostgreSQL (требуется отдельно)
# brew install postgresql
# brew services start postgresql

# Создаем пользователя и базу данных
createuser -s airflow
createdb -O airflow airflow
psql -d airflow -c "ALTER USER airflow PASSWORD 'airflow';"

# Генерируем конфигурацию
python setup_airflow_config.py --postgres

# Запускаем Airflow
./start_airflow_postgres_8082.sh

# Веб-интерфейс: http://localhost:8082
```

#### Вариант 3: Docker (изолированный)
```bash
# Генерируем конфигурацию
python setup_airflow_config.py --docker

# Запускаем в Docker
./start_airflow_docker_8083.sh

# Веб-интерфейс: http://localhost:8083
```

### Проверка системы
```bash
# Автоматическое тестирование всех режимов
python test_all_configurations.py
```

### Остановка сервисов
```bash
# SQLite
./stop_airflow_sqlite.sh

# PostgreSQL 
./stop_airflow_postgres.sh

# Docker
./stop_airflow_docker.sh
```

### Вход в систему
- **Логин:** `admin`
- **Пароль:** `admin`

### Размещение DAG-файлов
Поместите ваши DAG-файлы в директорию:
```
ml-pipeline-project/dags/
```

Все пути формируются программно и являются абсолютными!

### Помощь и диагностика
```bash
# Просмотр логов
tail -f logs/scheduler_*.log
tail -f logs/webserver_*.log

# Проверка статуса процессов
ps aux | grep airflow

# Проверка портов
lsof -i :8081 # SQLite
lsof -i :8082 # PostgreSQL 
lsof -i :8083 # Docker
```

## Все готово!
Система автоматически:
- Создает виртуальное окружение
- Устанавливает все зависимости
- Формирует абсолютные пути программно
- Настраивает базу данных
- Запускает веб-интерфейс на нужном порту
