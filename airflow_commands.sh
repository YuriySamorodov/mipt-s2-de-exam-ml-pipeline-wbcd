# Команды для запуска задач Airflow
# Используйте эти команды для тестирования и отладки отдельных задач

# Переменные окружения
export AIRFLOW_HOME=./airflow
export AIRFLOW__CORE__DAGS_FOLDER=./dags
export AIRFLOW__CORE__LOGS_FOLDER=./logs

# Общие команды Airflow

# Инициализация базы данных Airflow
airflow db init

# Создание администратора
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Список DAG-ов
airflow dags list

# Подробности о DAG
airflow dags show breast_cancer_ml_pipeline

# Список задач в DAG
airflow tasks list breast_cancer_ml_pipeline

# Тестирование конкретных задач

# 1. Проверка системы
airflow tasks test breast_cancer_ml_pipeline health_check 2024-01-01

# 2. Загрузка и валидация данных
airflow tasks test breast_cancer_ml_pipeline load_and_validate_data 2024-01-01

# 3. Предобработка данных
airflow tasks test breast_cancer_ml_pipeline preprocess_data 2024-01-01

# 4. Обучение модели
airflow tasks test breast_cancer_ml_pipeline train_model 2024-01-01

# 5. Оценка модели
airflow tasks test breast_cancer_ml_pipeline evaluate_model 2024-01-01

# 6. Сохранение результатов
airflow tasks test breast_cancer_ml_pipeline save_results 2024-01-01

# 7. Очистка
airflow tasks test breast_cancer_ml_pipeline cleanup 2024-01-01

# Запуск полного DAG
airflow dags trigger breast_cancer_ml_pipeline

# Запуск DAG с конкретной датой
airflow dags trigger breast_cancer_ml_pipeline --exec-date 2024-01-01

# Проверка состояния DAG
airflow dags state breast_cancer_ml_pipeline 2024-01-01

# Просмотр логов задачи
airflow tasks logs breast_cancer_ml_pipeline load_and_validate_data 2024-01-01

# Установка переменных Airflow
airflow variables set use_hyperparameter_tuning true
airflow variables set upload_to_cloud false
airflow variables set cleanup_max_age_days 30

# Просмотр переменных
airflow variables list

# Удаление переменной
airflow variables delete variable_name

# Создание подключений (connections)
airflow connections add 'gcs_default' \
    --conn-type 'google_cloud_platform' \
    --conn-extra '{"extra__google_cloud_platform__project": "your-project", "extra__google_cloud_platform__key_path": "/path/to/keyfile.json"}'

# Просмотр подключений
airflow connections list

# Запуск веб-сервера (в отдельном терминале)
airflow webserver --port 8080

# Запуск планировщика (в отдельном терминале)
airflow scheduler

# Остановка всех процессов Airflow
pkill -f airflow

# Для Docker Compose

# Запуск Airflow с помощью Docker Compose
docker-compose up airflow-init
docker-compose up -d

# Просмотр логов
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# Выполнение команд внутри контейнера
docker-compose exec airflow-webserver airflow dags list
docker-compose exec airflow-webserver airflow tasks test breast_cancer_ml_pipeline health_check 2024-01-01

# Остановка сервисов
docker-compose down

# Полная очистка (включая volumes)
docker-compose down --volumes --remove-orphans
