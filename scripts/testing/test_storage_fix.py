#!/usr/bin/env python3
"""
Тест для проверки исправления ошибки типов в storage_manager.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

# Добавляем корневую папку в путь
sys.path.append(os.path.join(os.path.dirname(__file__), ../..)) # os.path.dirname(os.path.abspath(__file__)))

from src.etl.storage_manager import StorageManager

def test_storage_manager_with_wrong_types():
"""Тестируем StorageManager с неправильными типами параметров."""

print(" Тестирование StorageManager с неправильными типами...")

storage_manager = StorageManager()

# Тестовые результаты
test_results = {
'timestamp': '2025-06-17T05:40:00',
'model_type': 'LogisticRegression',
'metrics': {'accuracy': 0.97, 'f1_score': 0.96}
}

print("\n1. Тест с правильными параметрами:")
try:
result = storage_manager.save_pipeline_results(
results=test_results,
model_path=None, # Правильно - None
metrics_path=None # Правильно - None
)
print(f" Успешно: {result}")
except Exception as e:
print(f" Ошибка: {e}")

print("\n2. Тест с неправильным типом model_path (словарь):")
try:
result = storage_manager.save_pipeline_results(
results=test_results,
model_path={'invalid': 'dict'}, # Неправильно - словарь вместо строки
metrics_path=None
)
print(f" Обработано корректно: {result}")
except Exception as e:
print(f" Ошибка: {e}")

print("\n3. Тест с неправильным типом metrics_path (список):")
try:
result = storage_manager.save_pipeline_results(
results=test_results,
model_path=None,
metrics_path=['invalid', 'list'] # Неправильно - список вместо строки
)
print(f" Обработано корректно: {result}")
except Exception as e:
print(f" Ошибка: {e}")

print("\n4. Тест с несуществующим файлом (строка):")
try:
result = storage_manager.save_pipeline_results(
results=test_results,
model_path="/path/to/nonexistent/file.joblib", # Правильный тип, но файл не существует
metrics_path=None
)
print(f" Обработано корректно: {result}")
except Exception as e:
print(f" Ошибка: {e}")

if __name__ == "__main__":
test_storage_manager_with_wrong_types()
print("\n Тестирование завершено!")
