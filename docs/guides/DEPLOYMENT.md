# Инструкции по развертыванию ML Pipeline

## Быстрый старт

### 1. Подготовка окружения

```bash
# Клонируйте проект
git clone <repository-url>
cd ml-pipeline-project

# Создайте виртуальное окружение
make setup

# Активируйте виртуальное окружение
source venv/bin/activate # Linux/Mac
```

### 2. Копирование данных

```bash
# Скопируйте файл данных в нужное место
cp path/to/wdbc.data.txt data/wdbc.data.csv
```

### 3. Настройка конфигурации

```bash
# Скопируйте пример переменных окружения
cp .env.example .env

# Отредактируйте .env файл при необходимости
nano .env
```

### 4. Демонстрация работы

```bash
# Запустите демонстрацию пайплайна
python demo_pipeline.py

# Или используйте Makefile
make demo
```

## Развертывание с Apache Airflow

### Локальное развертывание

```bash
# Инициализация Airflow
make airflow-init

# Запуск Airflow
make airflow-start

# Откройте веб-интерфейс: http://localhost:8080
# Логин: admin, Пароль: admin
```

### Docker развертывание

```bash
# Запуск всей инфраструктуры
docker-compose up -d

# Просмотр логов
docker-compose logs -f airflow-webserver

# Остановка
docker-compose down
```

## Облачное развертывание

### Google Cloud Platform

1. **Создайте сервисный аккаунт:**
- Перейдите в Google Cloud Console
- IAM & Admin > Service Accounts
- Создайте новый сервисный аккаунт с ролью Storage Admin
- Скачайте JSON ключ

2. **Настройте учетные данные:**
```bash
# Сохраните JSON ключ как config/gcs-credentials.json
export GOOGLE_APPLICATION_CREDENTIALS=config/gcs-credentials.json
```

3. **Создайте bucket:**
```bash
gsutil mb gs://your-ml-pipeline-bucket
```

### Amazon Web Services

1. **Создайте IAM пользователя:**
- AWS Console > IAM > Users
- Создайте пользователя с правами S3

2. **Настройте учетные данные:**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_BUCKET_NAME=your-bucket-name
```

3. **Создайте S3 bucket:**
```bash
aws s3 mb s3://your-ml-pipeline-bucket
```

## Мониторинг и логирование

### Включение дополнительных сервисов

```bash
# Запуск с Jupyter Notebook
docker-compose --profile jupyter up -d

# Запуск с мониторингом (Grafana + Prometheus)
docker-compose --profile monitoring up -d

# Jupyter: http://localhost:8888 (token: ml-pipeline-token)
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### Настройка уведомлений

1. **Email уведомления в Airflow:**
```python
# В airflow.cfg
[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = your-email@gmail.com
smtp_password = your-app-password
smtp_port = 587
smtp_mail_from = your-email@gmail.com
```

2. **Slack интеграция:**
```python
# Добавьте в DAG
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

slack_failed_task = SlackWebhookOperator(
task_id="slack_failed",
http_conn_id="slack_default",
message="ML Pipeline failed!",
trigger_rule="one_failed"
)
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
make test

# Тесты с покрытием
pytest tests/ --cov=etl --cov-report=html

# Тест конкретного модуля
pytest tests/test_data_loader.py -v
```

### Тестирование Airflow DAG

```bash
# Тест структуры DAG
python dags/ml_pipeline_dag.py

# Тест отдельной задачи
airflow tasks test breast_cancer_ml_pipeline health_check 2024-01-01
```

## Продакшн развертывание

### Рекомендуемая архитектура

```

Load Balancer Airflow Web Airflow
Server Scheduler



PostgreSQL Redis
(Metadata) (Celery)



Workers Cloud Storage
(Kubernetes) (GCS/S3)

```

### Kubernetes развертывание

1. **Создайте namespace:**
```bash
kubectl create namespace ml-pipeline
```

2. **Создайте ConfigMap:**
```bash
kubectl create configmap ml-config --from-file=config/config.yaml -n ml-pipeline
```

3. **Создайте Secret:**
```bash
kubectl create secret generic ml-secrets \
--from-file=gcs-credentials=config/gcs-credentials.json \
-n ml-pipeline
```

4. **Примените манифесты:**
```bash
kubectl apply -f k8s/ -n ml-pipeline
```

### Безопасность

1. **Переменные окружения:**
- Никогда не коммитьте .env файлы
- Используйте secret management (Vault, AWS Secrets Manager)
- Ротируйте ключи доступа

2. **Сетевая безопасность:**
- Используйте VPC/VNET
- Настройте файрволы
- Включите HTTPS

3. **Мониторинг безопасности:**
- Логируйте все доступы
- Мониторьте аномальную активность
- Настройте алерты

## Резервное копирование

### Backup стратегия

1. **База данных Airflow:**
```bash
# PostgreSQL backup
pg_dump airflow > backup_$(date +%Y%m%d).sql
```

2. **Модели и артефакты:**
```bash
# Автоматический backup в облако
python -c "
from etl.storage_manager import StorageManager
sm = StorageManager
sm.save_pipeline_results({}, upload_to_cloud=True)
"
```

3. **Код проекта:**
```bash
# Git backup
git bundle create backup.bundle --all
```

## Масштабирование

### Горизонтальное масштабирование

1. **Airflow Workers:**
```bash
# Docker Swarm
docker service scale airflow_worker=5

# Kubernetes
kubectl scale deployment airflow-worker --replicas=5
```

2. **База данных:**
- Используйте managed services (RDS, Cloud SQL)
- Настройте read replicas
- Включите автоматическое масштабирование

### Вертикальное масштабирование

1. **CPU/Memory:**
```yaml
# docker-compose.yml
resources:
limits:
cpus: '2.0'
memory: 4G
reservations:
cpus: '1.0'
memory: 2G
```

2. **Storage:**
- Используйте SSD диски
- Настройте автоматическое расширение
- Мониторьте использование диска

## Устранение неполадок

### Частые проблемы

1. **Airflow не запускается:**
```bash
# Проверьте логи
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# Сбросьте базу данных
airflow db reset
```

2. **Ошибки импорта Python:**
```bash
# Проверьте PYTHONPATH
export PYTHONPATH=/path/to/project:$PYTHONPATH

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

3. **Проблемы с правами доступа:**
```bash
# Docker
docker-compose exec airflow-webserver chmod -R 755 /opt/airflow/dags

# Локально
chmod +x demo_pipeline.py
```

### Логи и диагностика

1. **Включите debug логирование:**
```bash
export LOG_LEVEL=DEBUG
python demo_pipeline.py
```

2. **Проверьте Airflow логи:**
```bash
# Логи задачи
airflow tasks logs breast_cancer_ml_pipeline load_data 2024-01-01

# Логи DAG
tail -f logs/scheduler/2024-01-01/breast_cancer_ml_pipeline.py.log
```

3. **Мониторинг ресурсов:**
```bash
# Использование CPU/Memory
docker stats

# Использование диска
df -h
du -sh results/
```

## Обновление и миграция

### Обновление зависимостей

```bash
# Обновите requirements.txt
pip-compile requirements.in

# Тестируйте в отдельном окружении
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
make test
```

### Миграция данных

```bash
# Backup текущих данных
cp -r results/ backup_results_$(date +%Y%m%d)/

# Запустите миграцию
python scripts/migrate_data.py

# Проверьте результат
python scripts/validate_migration.py
```

---

**Для получения поддержки обратитесь к команде разработки или создайте Issue в GitHub репозитории.**
