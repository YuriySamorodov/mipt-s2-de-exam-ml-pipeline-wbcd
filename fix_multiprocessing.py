#!/usr/bin/env python3
"""
Скрипт для исправления LocalExecutor на macOS
"""
import multiprocessing
import os
import sys

# Принудительно устанавливаем spawn метод для macOS
if sys.platform == 'darwin': # macOS
multiprocessing.set_start_method('spawn', force=True)

# Устанавливаем переменные для macOS
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
os.environ['AIRFLOW__CORE__EXECUTOR'] = 'LocalExecutor'
os.environ['AIRFLOW__CORE__PARALLELISM'] = '2' # Еще больше уменьшаем
os.environ['AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG'] = '2'

print(" Настройки multiprocessing для macOS установлены")
print(f" Start method: {multiprocessing.get_start_method()}")
print(f" Parallelism: 2")
print(f" OBJC_DISABLE_INITIALIZE_FORK_SAFETY: YES")

# Теперь импортируем Airflow
try:
from airflow.cli import cli_parser
from airflow.cli.commands.scheduler_command import scheduler

print(" Airflow импортирован успешно")

# Запускаем scheduler
print(" Запуск LocalExecutor с исправленными настройками...")

# Создаем аргументы для scheduler
class Args:
daemon = False
pid = None
stdout = None
stderr = None
log_file = None

args = Args()
scheduler(args)

except Exception as e:
print(f" Ошибка: {e}")
sys.exit(1)
