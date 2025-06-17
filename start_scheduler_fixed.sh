#!/bin/bash
# Скрипт для запуска Airflow scheduler с патчем LocalExecutor

echo " Запуск Airflow Scheduler с патчем LocalExecutor..."

# Активируем окружение
source venv/bin/activate

# Устанавливаем переменные окружения
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"

# Критически важные настройки для macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYTHONPATH="$PWD/scripts/airflow:$PYTHONPATH"

# Применяем патч и запускаем scheduler
python -c "
import sys
import multiprocessing
import os

# Устанавливаем fork для macOS
if sys.platform == 'darwin':
multiprocessing.set_start_method('fork', force=True)

# Патчим LocalExecutor перед импортом Airflow
try:
from airflow.executors import local_executor

# Если проблема в QueuedLocalWorker, пропатчим его
if hasattr(local_executor, 'QueuedLocalWorker'):
worker_class = local_executor.QueuedLocalWorker
if not hasattr(worker_class, 'wrapper'):
setattr(worker_class, 'wrapper', lambda self: None)
print(' Патч LocalExecutor применен')

# Запускаем scheduler
from airflow.cli.commands.scheduler_command import scheduler
from airflow.configuration import conf
import argparse

# Создаем аргументы как у CLI
parser = argparse.ArgumentParser()
parser.add_argument('--daemon', action='store_true', default=False)
parser.add_argument('--num-runs', type=int, default=-1)
parser.add_argument('--do-pickle', action='store_true', default=False)
parser.add_argument('--pid', default=None)
parser.add_argument('--skip-serve-logs', action='store_true', default=False)
parser.add_argument('--subdir', default=None)
parser.add_argument('--verbose', action='store_true', default=False)
parser.add_argument('--log-file', default=None)

args = parser.parse_args([])

print(' Запуск scheduler...')
scheduler(args)

except Exception as e:
print(f' Ошибка: {e}')
import traceback
traceback.print_exc()
"
