#!/bin/bash
# Ярлык для запуска Airflow PostgreSQL
echo " Запуск Airflow PostgreSQL (LocalExecutor, порт 8082)..."
exec "$(dirname "$0")/scripts/airflow/start_airflow_postgres_8082.sh" "$@"
