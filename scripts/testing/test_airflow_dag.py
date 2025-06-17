#!/usr/bin/env python3
"""
Тест функций DAG без запуска Airflow.
"""
import sys
import os
from pathlib import Path

# Добавляем путь к модулям ETL
PROJECT_ROOT = Path(__file__).parent
sys.path.append(os.path.join(os.path.dirname(__file__), ../..)) # str(PROJECT_ROOT))
sys.path.append(os.path.join(os.path.dirname(__file__), ../..)) # str(PROJECT_ROOT / "etl"))

# Импортируем функции из DAG
from dags.ml_pipeline_dag import (
load_and_validate_data,
data_quality_check,
preprocess_data,
train_model,
evaluate_model
)

def test_dag_functions():
"""Тестируем функции DAG по очереди."""

# Создаем mock context
class MockTaskInstance:
def __init__(self):
self.xcom_data = {}

def xcom_push(self, key, value):
self.xcom_data[key] = value
print(f"XCom PUSH: {key} = {value}")

def xcom_pull(self, task_ids=None, key=None):
if task_ids and key:
full_key = f"{task_ids}_{key}"
return self.xcom_data.get(full_key, self.xcom_data.get(key))
return self.xcom_data.get(key)

mock_ti = MockTaskInstance()
context = {'task_instance': mock_ti}

print("=" * 60)
print("ТЕСТИРОВАНИЕ ФУНКЦИЙ AIRFLOW DAG")
print("=" * 60)

try:
# 1. Тест загрузки и валидации данных
print("\n1. Тестирование load_and_validate_data...")
result1 = load_and_validate_data(**context)
print(f" Результат: {result1}")

# 2. Тест проверки качества данных
print("\n2. Тестирование data_quality_check...")
result2 = data_quality_check(**context)
print(f" Результат: {result2}")

# 3. Тест предобработки данных
print("\n3. Тестирование preprocess_data...")
result3 = preprocess_data(**context)
print(f" Результат: {result3}")

# 4. Тест обучения модели
print("\n4. Тестирование train_model...")
result4 = train_model(**context)
print(f" Результат: {result4}")

# 5. Тест оценки модели
print("\n5. Тестирование evaluate_model...")
result5 = evaluate_model(**context)
print(f" Результат: {result5}")

print("\n" + "=" * 60)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
print("=" * 60)

return True

except Exception as e:
print(f"\nОШИБКА: {str(e)}")
import traceback
traceback.print_exc()
return False

if __name__ == "__main__":
success = test_dag_functions()
sys.exit(0 if success else 1)
