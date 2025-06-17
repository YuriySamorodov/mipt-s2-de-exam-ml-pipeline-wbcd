#!/bin/bash

# Complete Airflow 3.0.2 + CeleryExecutor Startup Script
# This script ensures all services start with correct configuration

echo "=============================================="
echo "Starting Airflow 3.0.2 with CeleryExecutor"
echo "=============================================="

# Set working directory
cd "/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project"

# Activate virtual environment
source venv/bin/activate

# Set environment variables with proper configuration
export AIRFLOW_HOME="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite://///Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/airflow/airflow.db"
export AIRFLOW__CORE__DAGS_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Remove any conflicting environment variables to ensure config file is used
unset AIRFLOW__CORE__EXECUTOR
unset AIRFLOW__WEBSERVER__WORKERS
unset AIRFLOW__WEBSERVER__WORKER_TIMEOUT
unset AIRFLOW__WEBSERVER__SECRET_KEY
unset AIRFLOW__CORE__INTERNAL_API_URL

echo "Step 1: Checking Redis..."
redis-cli ping
if [ $? -ne 0 ]; then
echo "Starting Redis..."
brew services start redis
sleep 3
redis-cli ping
fi

echo "Step 2: Verifying Airflow configuration..."
echo "Executor: $(airflow config get-value core executor)"
echo "Broker URL: $(airflow config get-value celery broker_url)"
echo "Internal API URL: $(airflow config get-value core internal_api_url)"

echo "Step 3: Reserializing DAGs..."
airflow dags reserialize > /dev/null 2>&1

echo "Step 4: Starting services..."

echo " Starting Celery Worker..."
nohup python -m celery -A airflow.providers.celery.executors.celery_executor worker \
--loglevel=info --concurrency=4 --hostname=celery-worker@localhost --queues=default \
> airflow/logs/celery-worker-restart.log 2>&1 &
CELERY_PID=$!
echo " Celery Worker PID: $CELERY_PID"
sleep 5

echo " Starting Airflow Scheduler..."
nohup airflow scheduler > airflow/logs/scheduler-restart.log 2>&1 &
SCHEDULER_PID=$!
echo " Scheduler PID: $SCHEDULER_PID"
sleep 5

echo " Starting Airflow API Server..."
nohup airflow api-server -p 8082 > airflow/logs/api-server-restart.log 2>&1 &
API_SERVER_PID=$!
echo " API Server PID: $API_SERVER_PID"
sleep 5

echo "=============================================="
echo "All services started successfully!"
echo "=============================================="

# Test service health
echo "Step 5: Testing service health..."
sleep 3

# Check if processes are running
echo "Running processes:"
ps aux | grep -E "(airflow|celery)" | grep -v grep | head -5

# Test API server health
echo ""
echo "API Health Check:"
curl -s http://localhost:8082/api/v2/monitor/health | python -m json.tool 2>/dev/null || echo "API server starting..."

echo ""
echo "=============================================="
echo "Service Information:"
echo " - Web UI: http://localhost:8082"
echo " - Health: http://localhost:8082/api/v2/monitor/health"
echo " - Auth: admin/admin (SimpleAuthManager)"
echo ""
echo "Process IDs:"
echo " - Celery Worker: $CELERY_PID"
echo " - Scheduler: $SCHEDULER_PID"
echo " - API Server: $API_SERVER_PID"
echo ""
echo "Log files:"
echo " - Celery: tail -f airflow/logs/celery-worker-restart.log"
echo " - Scheduler: tail -f airflow/logs/scheduler-restart.log"
echo " - API Server: tail -f airflow/logs/api-server-restart.log"
echo ""
echo "Commands:"
echo " - Trigger DAG: airflow dags trigger breast_cancer_ml_pipeline"
echo " - Check DAG status: airflow dags state breast_cancer_ml_pipeline"
echo " - Stop services: pkill -f 'airflow|celery'"
echo "=============================================="
