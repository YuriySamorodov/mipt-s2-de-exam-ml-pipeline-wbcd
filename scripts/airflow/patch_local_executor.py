#!/usr/bin/env python3
"""
Патч для исправления LocalExecutor на macOS с Python 3.12
"""

import multiprocessing
import sys
import os

def patch_local_executor():
"""Применяет патч для LocalExecutor"""

# Устанавливаем spawn метод для multiprocessing
if sys.platform == 'darwin': # macOS
multiprocessing.set_start_method('fork', force=True)

# Патчим QueuedLocalWorker
try:
from airflow.executors.local_executor import QueuedLocalWorker

# Если у класса нет атрибута wrapper, добавляем его
if not hasattr(QueuedLocalWorker, 'wrapper'):
def dummy_wrapper(self):
return None
QueuedLocalWorker.wrapper = dummy_wrapper

print(" LocalExecutor патч применен успешно")
except ImportError as e:
print(f" Не удалось импортировать QueuedLocalWorker: {e}")
except Exception as e:
print(f" Ошибка применения патча: {e}")

if __name__ == "__main__":
patch_local_executor()
