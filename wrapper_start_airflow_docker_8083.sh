#!/bin/bash
# Ярлык для запуска Airflow Docker
echo " Запуск Airflow Docker (LocalExecutor + PostgreSQL, порт 8083)..."
exec "$(dirname "$0")/scripts/airflow/start_airflow_docker_8083.sh" "$@"
