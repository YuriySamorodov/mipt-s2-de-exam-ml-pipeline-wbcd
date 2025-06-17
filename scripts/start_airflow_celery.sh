#!/bin/bash

# Airflow Celery Setup Script
# This script starts all Airflow services with CeleryExecutor

# Set working directory
cd "/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export AIRFLOW_HOME="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite://///Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/airflow/airflow.db"
export AIRFLOW__CORE__DAGS_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__INTERNAL_API_URL="http://localhost:8082"

# Remove any conflicting environment variables
unset AIRFLOW__CORE__EXECUTOR
unset AIRFLOW__WEBSERVER__WORKERS
unset AIRFLOW__WEBSERVER__WORKER_TIMEOUT
unset AIRFLOW__WEBSERVER__SECRET_KEY

echo "Starting Redis..."
brew services start redis

echo "Checking Redis connection..."
redis-cli ping

echo "Current executor configuration:"
airflow config get-value core executor

echo "Starting Celery Worker..."
AIRFLOW__CORE__INTERNAL_API_URL="http://localhost:8082" nohup airflow celery worker --loglevel=info > airflow/logs/celery-worker.log 2>&1 &
CELERY_PID=$!
echo "Celery Worker PID: $CELERY_PID"

sleep 5

echo "Starting Airflow Scheduler..."
nohup airflow scheduler > airflow/logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "Scheduler PID: $SCHEDULER_PID"

sleep 5

echo "Starting Airflow Webserver..."
nohup airflow api-server -p 8082 > airflow/logs/webserver.log 2>&1 &
WEBSERVER_PID=$!
echo "Webserver PID: $WEBSERVER_PID"

echo "All services started!"
echo "Webserver: http://localhost:8082"
echo "Flower (optional): airflow celery flower"
echo ""
echo "Process IDs:"
echo "Celery Worker: $CELERY_PID"
echo "Scheduler: $SCHEDULER_PID"
echo "Webserver: $WEBSERVER_PID"
echo ""
echo "To stop services, run: ./scripts/stop_airflow.sh"
echo "To monitor logs:"
echo " tail -f airflow/logs/celery-worker.log"
echo " tail -f airflow/logs/scheduler.log"
echo " tail -f airflow/logs/webserver.log"
