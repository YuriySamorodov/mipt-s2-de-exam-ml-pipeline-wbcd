#!/usr/bin/env python3
"""
Специальный скрипт для запуска Airflow scheduler с исправлениями для LocalExecutor на macOS
"""

import os
import sys
import subprocess
import multiprocessing

def fix_multiprocessing():
"""Исправляет настройки multiprocessing для macOS"""
if hasattr(multiprocessing, 'set_start_method'):
try:
multiprocessing.set_start_method('spawn', force=True)
print(" Multiprocessing start method установлен в 'spawn'")
except RuntimeError as e:
print(f" Multiprocessing уже настроен: {e}")

# Дополнительные настройки для macOS
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
os.environ['AIRFLOW__CORE__MP_START_METHOD'] = 'spawn'

def main():
"""Запуск scheduler с исправлениями"""
print(" Запуск Airflow Scheduler с исправлениями для LocalExecutor")

# Исправляем multiprocessing
fix_multiprocessing()

# Устанавливаем переменные окружения
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
airflow_home = os.path.join(project_dir, 'airflow')

os.environ['AIRFLOW_HOME'] = airflow_home
os.environ['AIRFLOW__CORE__EXECUTOR'] = 'LocalExecutor'
os.environ['AIRFLOW__DATABASE__SQL_ALCHEMY_CONN'] = 'postgresql+psycopg2://airflow:airflow@localhost:5432/airflow'
os.environ['AIRFLOW__WEBSERVER__WEB_SERVER_PORT'] = '8082'

print(f" AIRFLOW_HOME: {airflow_home}")
print(f" Database: PostgreSQL")
print(f" Executor: LocalExecutor (исправленный)")

# Запускаем scheduler
cmd = [sys.executable, '-m', 'airflow', 'scheduler']
print(f" Команда: {' '.join(cmd)}")

try:
subprocess.run(cmd, check=True)
except KeyboardInterrupt:
print("\n Scheduler остановлен пользователем")
except Exception as e:
print(f" Ошибка запуска scheduler: {e}")
return 1

return 0

if __name__ == '__main__':
sys.exit(main())
