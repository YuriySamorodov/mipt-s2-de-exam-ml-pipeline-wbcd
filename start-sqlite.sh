#!/bin/bash
# Ярлык для запуска Airflow SQLite
echo " Запуск Airflow SQLite (SequentialExecutor, порт 8081)..."
exec "$(dirname "$0")/scripts/airflow/start_airflow_sqlite_8081.sh" "$@"
