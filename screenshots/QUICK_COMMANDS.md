# Быстрые команды для создания скриншотов

> Этот файл содержит все команды, необходимые для создания полного набора скриншотов ML Pipeline

## Настройка и запуск системы

```bash
# Клонирование и переход в проект
cd ml-pipeline-project

# Запуск системы
docker-compose up -d

# Ожидание полного запуска (2-3 минуты)
sleep 180

# Проверка статуса
docker ps -a
```

## Команды для скриншотов

### 1. Setup & Monitoring (`screenshots/setup/`, `screenshots/monitoring/`)

```bash
# Статус контейнеров
docker ps -a

# Использование ресурсов
docker stats --no-stream

# Образы Docker
docker images | grep ml-pipeline

# Статус docker-compose
docker-compose ps

# Логи системы
docker logs ml-pipeline-project-airflow-webserver-1
docker logs ml-pipeline-project-postgres-1

# Проверка портов
netstat -tulpn | grep :8080
netstat -tulpn | grep :5432

# Health checks
docker inspect ml-pipeline-project-airflow-webserver-1 | grep -A 10 "Health"
```

### 2. Airflow Interface (`screenshots/airflow/`)

```bash
# Открыть Airflow Web UI
open http://localhost:8080

# Или curl для проверки доступности
curl -I http://localhost:8080
```

**URLs для скриншотов:**
- Главная: http://localhost:8080
- DAG Graph: http://localhost:8080/graph?dag_id=breast_cancer_ml_pipeline
- DAG Tree: http://localhost:8080/tree?dag_id=breast_cancer_ml_pipeline
- Admin Panel: http://localhost:8080/admin

### 3. Database (`screenshots/database/`)

```bash
# Подключение к PostgreSQL
docker exec -it ml-pipeline-project-postgres-1 psql -U ml_user -d ml_pipeline

# SQL команды для скриншотов:
\l # Список баз данных
\dt # Список таблиц
\d breast_cancer_data # Структура таблицы

SELECT * FROM breast_cancer_data LIMIT 10;
SELECT diagnosis, COUNT(*) FROM breast_cancer_data GROUP BY diagnosis;
SELECT COUNT(*) FROM breast_cancer_data;

\q # Выход
```

### 4. Results & Files (`screenshots/results/`)

```bash
# Файлы результатов в контейнере
docker exec -it ml-pipeline-project-airflow-webserver-1 ls -la /opt/airflow/results/

# Модели
docker exec -it ml-pipeline-project-airflow-webserver-1 ls -la /opt/airflow/results/models/

# Метрики
docker exec -it ml-pipeline-project-airflow-webserver-1 cat /opt/airflow/results/metrics/model_metrics.json

# Графики (если есть)
docker exec -it ml-pipeline-project-airflow-webserver-1 ls -la /opt/airflow/results/plots/

# Копирование файлов на хост (для просмотра)
docker cp ml-pipeline-project-airflow-webserver-1:/opt/airflow/results/. ./temp_results/
```

## Последовательность создания скриншотов

### Этап 1: Базовая установка
1. **docker-compose-up.png** - `docker-compose up -d`
2. **containers-status.png** - `docker ps -a`
3. **resource-usage.png** - `docker stats --no-stream`

### Этап 2: Airflow интерфейс
4. **airflow-home.png** - http://localhost:8080
5. **dag-overview.png** - Список DAG
6. **dag-graph.png** - График выполнения DAG
7. **task-logs.png** - Логи выполнения задач

### Этап 3: База данных
8. **postgres-connection.png** - Подключение к БД
9. **data-tables.png** - Таблицы и данные
10. **sql-queries.png** - Примеры запросов

### Этап 4: Результаты ML
11. **results-files.png** - Файлы результатов
12. **model-metrics.png** - Метрики модели
13. **ml-plots.png** - Графики и визуализации

### Этап 5: Мониторинг
14. **system-health.png** - Общее состояние системы
15. **error-logs.png** - Проверка отсутствия ошибок

## Очистка после демонстрации

```bash
# Остановка системы
docker-compose down

# Очистка volumes (опционально)
docker-compose down -v

# Удаление образов (опционально)
docker rmi ml-pipeline-airflow postgres:13

# Удаление временных файлов
rm -rf temp_results/
```

## Советы по качеству скриншотов

1. **Разрешение**: Минимум 1920x1080
2. **Браузер**: Используйте полноэкранный режим
3. **Терминал**: Увеличьте шрифт для лучшей читаемости
4. **Тайминг**: Дождитесь полной загрузки страниц
5. **Фокус**: Выделяйте важные элементы

## Проверка перед скриншотами

```bash
# Проверьте, что все сервисы работают
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Проверьте доступность Airflow
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080

# Проверьте PostgreSQL
docker exec ml-pipeline-project-postgres-1 pg_isready -U ml_user

# Если все OK - можно делать скриншоты!
echo " Система готова для создания скриншотов"
```
