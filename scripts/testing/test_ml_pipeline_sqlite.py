#!/usr/bin/env python3 
"""
Тестирование ML пайплайна без Airflow - только основная ETL логика
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

# Добавляем пути к модулям
PROJECT_ROOT = Path(__file__).parent
sys.path.append(os.path.join(os.path.dirname(__file__), ../..)) # str(PROJECT_ROOT))
sys.path.append(os.path.join(os.path.dirname(__file__), ../..)) # str(PROJECT_ROOT / "etl"))

def test_etl_pipeline():
"""Тестируем основные компоненты ETL пайплайна"""

print(" Тестирование компонентов ETL пайплайна")
print("=" * 50)

try:
# Импорт модулей
from src.etl.data_loader import DataLoader
from src.etl.data_preprocessor import DataPreprocessor 
from src.etl.model_trainer import ModelTrainer
from src.etl.metrics_calculator import MetricsCalculator
from src.etl.storage_manager import StorageManager
from src.etl.data_quality_controller import DataQualityController

print(" Все модули ETL успешно импортированы")

# Проверим наличие данных
data_path = PROJECT_ROOT / "data"
print(f" Проверяем директорию данных: {data_path}")

if data_path.exists():
data_files = list(data_path.glob("*.csv")) + list(data_path.glob("*.data*"))
print(f" Найдено файлов данных: {len(data_files)}")
for file in data_files:
print(f" - {file.name}")
else:
print(" Директория данных не найдена")
return False

# Тестируем DataLoader
print("\n Тестируем DataLoader...")
data_loader = DataLoader()
print(" DataLoader создан успешно")

# Тестируем DataQualityController
print("\n Тестируем DataQualityController...")
quality_controller = DataQualityController()
print(" DataQualityController создан успешно")

# Тестируем DataPreprocessor
print("\n Тестируем DataPreprocessor...")
preprocessor = DataPreprocessor()
print(" DataPreprocessor создан успешно")

# Тестируем ModelTrainer
print("\n Тестируем ModelTrainer...")
model_trainer = ModelTrainer()
print(" ModelTrainer создан успешно")

# Тестируем MetricsCalculator
print("\n Тестируем MetricsCalculator...")
metrics_calc = MetricsCalculator()
print(" MetricsCalculator создан успешно")

# Тестируем StorageManager
print("\n Тестируем StorageManager...")
storage_manager = StorageManager()
print(" StorageManager создан успешно")

return True

except ImportError as e:
print(f" Ошибка импорта: {e}")
return False
except Exception as e:
print(f" Ошибка инициализации: {e}")
return False

def test_sqlite_database():
"""Тестируем работу с SQLite базой данных"""

print("\n Тестируем работу с SQLite базой данных")
print("=" * 50)

try:
import sqlite3

# Создаем тестовую базу данных
db_path = PROJECT_ROOT / "ml_pipeline.db"
print(f" Путь к базе данных: {db_path}")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Создаем тестовую таблицу
cursor.execute('''
CREATE TABLE IF NOT EXISTS pipeline_test (
id INTEGER PRIMARY KEY AUTOINCREMENT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
test_name TEXT,
status TEXT,
details TEXT
)
''')

# Вставляем тестовые данные
cursor.execute('''
INSERT INTO pipeline_test (test_name, status, details)
VALUES (?, ?, ?)
''', ("sqlite_test", "success", "SQLite connection test passed"))

conn.commit()

# Проверяем данные
cursor.execute('SELECT * FROM pipeline_test ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()

if result:
print(f" SQLite база работает! Последняя запись: {result}")

conn.close()
return True

except Exception as e:
print(f" Ошибка работы с SQLite: {e}")
return False

def test_data_loading():
"""Тестируем загрузку данных Wisconsin Breast Cancer"""

print("\n Тестируем загрузку данных Wisconsin Breast Cancer")
print("=" * 50)

try:
# Ищем файл данных
data_files = [
PROJECT_ROOT / "data" / "wdbc.data",
PROJECT_ROOT / "data" / "wdbc.csv", 
PROJECT_ROOT.parent / "wdbc.data.txt"
]

data_file = None
for file_path in data_files:
if file_path.exists():
data_file = file_path
break

if not data_file:
print(" Файл данных Wisconsin Breast Cancer не найден")
print(" Ожидаемые пути:")
for path in data_files:
print(f" - {path}")
return False

print(f" Найден файл данных: {data_file}")

# Пробуем загрузить данные
if data_file.suffix == '.csv':
data = pd.read_csv(data_file)
else:
# Для .data файлов без заголовков
data = pd.read_csv(data_file, header=None)

print(f" Размер данных: {data.shape}")
print(f" Первые 5 строк:")
print(data.head())

return True

except Exception as e:
print(f" Ошибка загрузки данных: {e}")
return False

if __name__ == "__main__":
print(" Тестирование ML пайплайна с SQLite")
print("=" * 70)

results = []

# Тест 1: Основные компоненты ETL
results.append(("ETL Components", test_etl_pipeline()))

# Тест 2: SQLite база данных
results.append(("SQLite Database", test_sqlite_database()))

# Тест 3: Загрузка данных
results.append(("Data Loading", test_data_loading()))

# Результаты
print("\n Результаты тестирования:")
print("=" * 30)

all_passed = True
for test_name, passed in results:
status = " ПРОЙДЕН" if passed else " НЕ ПРОЙДЕН"
print(f"{test_name:20} | {status}")
if not passed:
all_passed = False

print("\n" + "=" * 30)
if all_passed:
print(" Все тесты пройдены! SQLite вариант работает корректно.")
else:
print(" Некоторые тесты не пройдены. Требуется дополнительная настройка.")
