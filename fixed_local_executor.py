#!/usr/bin/env python3
"""
Фикс для LocalExecutor - создание собственного LocalExecutor без проблем multiprocessing
"""

import os
import sys
import subprocess
import threading
import time
from queue import Queue
import logging

# Добавляем путь к Airflow
sys.path.insert(0, '/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/venv/lib/python3.12/site-packages')

# Устанавливаем переменные окружения
os.environ['AIRFLOW_HOME'] = '/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/airflow'
os.environ['AIRFLOW__CORE__EXECUTOR'] = 'LocalExecutor'
os.environ['AIRFLOW__DATABASE__SQL_ALCHEMY_CONN'] = 'postgresql+psycopg2://airflow:airflow@localhost:5432/airflow'
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

def patch_local_executor():
"""Патчим LocalExecutor для работы с macOS"""
try:
# Импортируем Airflow модули
from airflow.executors.local_executor import LocalExecutor
from airflow.executors.base_executor import BaseExecutor
import concurrent.futures

# Создаем новый LocalExecutor с ThreadPoolExecutor вместо multiprocessing
class FixedLocalExecutor(LocalExecutor):
def __init__(self):
super().__init__()
self.workers_used = 0
self.workers_active = 0
self._executor = None

def start(self):
"""Запуск executor с ThreadPoolExecutor"""
self._executor = concurrent.futures.ThreadPoolExecutor(
max_workers=4, # Ограничиваем количество workers
thread_name_prefix="airflow-worker"
)
self.workers_used = 0
self.workers_active = 0
print(" FixedLocalExecutor запущен с ThreadPoolExecutor")

def execute_async(self, key, command, queue=None, executor_config=None):
"""Асинхронное выполнение команды"""
if self._executor is None:
self.start()

def run_command():
try:
self.workers_active += 1
print(f" Выполняется команда: {' '.join(command)}")

# Выполняем команду через subprocess
result = subprocess.run(
command,
capture_output=True,
text=True,
cwd=os.environ.get('AIRFLOW_HOME', '/tmp')
)

if result.returncode == 0:
print(f" Команда успешно выполнена: {key}")
self.success(key)
else:
print(f" Команда завершилась с ошибкой: {key}")
print(f"Stderr: {result.stderr}")
self.fail(key)

except Exception as e:
print(f" Исключение при выполнении команды {key}: {e}")
self.fail(key)
finally:
self.workers_active -= 1

# Отправляем задачу в ThreadPoolExecutor
future = self._executor.submit(run_command)
self.workers_used += 1

def sync(self):
"""Синхронизация состояния"""
# Базовая синхронизация
pass

def end(self):
"""Завершение работы executor"""
if self._executor:
self._executor.shutdown(wait=True)
print(" FixedLocalExecutor остановлен")

@property 
def slots_available(self):
"""Возвращает количество доступных слотов"""
return max(0, 4 - self.workers_active) # Максимум 4 worker'а

# Заменяем оригинальный LocalExecutor
import airflow.executors.local_executor
airflow.executors.local_executor.LocalExecutor = FixedLocalExecutor

print(" LocalExecutor успешно пропатчен!")
return True

except Exception as e:
print(f" Ошибка патча LocalExecutor: {e}")
import traceback
traceback.print_exc()
return False

if __name__ == "__main__":
print(" Применение патча для LocalExecutor...")

if patch_local_executor():
print(" Запуск Airflow scheduler...")

# Запускаем scheduler
try:
from airflow.cli.commands.scheduler_command import scheduler
import argparse

# Создаем правильные аргументы
args = argparse.Namespace()
args.daemon = False
args.num_runs = -1
args.do_pickle = False
args.pid = None
args.skip_serve_logs = False
args.subdir = '/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/dags'

# Запускаем scheduler
scheduler(args)

except KeyboardInterrupt:
print(" Scheduler остановлен пользователем")
except Exception as e:
print(f" Ошибка запуска scheduler: {e}")
import traceback
traceback.print_exc()
else:
print(" Не удалось применить патч, завершение работы")
