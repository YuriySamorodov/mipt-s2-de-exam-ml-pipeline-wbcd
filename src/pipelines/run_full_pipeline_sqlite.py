#!/usr/bin/env python3
"""
Запуск полного ML пайплайна с SQLite (без Airflow)
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Добавляем пути к модулям
PROJECT_ROOT = Path(__file__).parent
sys.path.append(os.path.join(os.path.dirname(__file__), ..)) # str(PROJECT_ROOT))
sys.path.append(os.path.join(os.path.dirname(__file__), ..)) # str(PROJECT_ROOT / "etl"))
sys.path.append(os.path.join(os.path.dirname(__file__), ..)) # str(PROJECT_ROOT / "config"))

def run_full_pipeline():
"""Запускаем полный ML пайплайн"""

print(" Запуск полного ML пайплайна с SQLite")
print("=" * 60)

try:
# Импорт всех модулей
from src.etl.data_loader import DataLoader
from src.etl.data_preprocessor import DataPreprocessor
from src.etl.model_trainer import ModelTrainer
from src.etl.metrics_calculator import MetricsCalculator
from src.etl.storage_manager import StorageManager
from src.etl.data_quality_controller import DataQualityController

print(" Все модули успешно импортированы")

# Инициализируем компоненты
data_loader = DataLoader()
quality_controller = DataQualityController()
preprocessor = DataPreprocessor()
model_trainer = ModelTrainer()
metrics_calc = MetricsCalculator()
storage_manager = StorageManager()

print(" Все компоненты инициализированы")

# Шаг 1: Загрузка данных
print("\n Шаг 1: Загрузка данных...")

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
raise FileNotFoundError("Файл данных Wisconsin Breast Cancer не найден")

# Загружаем данные через DataLoader
data = data_loader.load_data(str(data_file))
print(f" Данные загружены: {data.shape}")

# Шаг 2: Контроль качества данных
print("\n Шаг 2: Контроль качества данных...")
quality_report = quality_controller.run_comprehensive_checks(data)

if quality_report['overall_score'] >= 70:
print(" Качество данных соответствует требованиям")
print(f" - Общий балл качества: {quality_report['overall_score']:.1f}")
print(f" - Всего записей: {quality_report['basic_statistics']['row_count']}")
print(f" - Пропущенных значений: {quality_report['missing_values']['total_missing']}")
print(f" - Дубликатов: {quality_report['duplicates']['duplicate_count']}")
else:
print(" Обнаружены проблемы с качеством данных")
print(f" - Общий балл качества: {quality_report['overall_score']:.1f}")
print(" - Продолжаем выполнение...")

# Шаг 3: Предобработка данных
print("\n Шаг 3: Предобработка данных...")
X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(data)

print(f" Данные подготовлены для обучения:")
print(f" - Обучающая выборка: {X_train.shape}")
print(f" - Тестовая выборка: {X_test.shape}")

# Шаг 4: Обучение модели
print("\n Шаг 4: Обучение модели...")
model = model_trainer.train_model(X_train, y_train)

print(" Модель обучена успешно")
print(f" - Тип модели: {type(model).__name__}")

# Шаг 5: Оценка модели
print("\n Шаг 5: Оценка модели...")
predictions = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

metrics = metrics_calc.calculate_basic_metrics(y_test, predictions)

print(" Результаты:")
print(f" - Точность: {metrics['accuracy']:.4f}")
print(f" - Precision: {metrics['precision']:.4f}")
print(f" - Recall: {metrics['recall']:.4f}")
print(f" - F1-score: {metrics['f1_score']:.4f}")
if 'auc_roc' in metrics:
print(f" - AUC-ROC: {metrics['auc_roc']:.4f}") 

# Шаг 6: Сохранение результатов
print("\n Шаг 6: Сохранение результатов...")

# Сохраняем модель и метрики
results = {
'timestamp': datetime.now().isoformat(),
'model_type': type(model).__name__,
'metrics': metrics,
'data_shape': data.shape,
'train_shape': X_train.shape,
'test_shape': X_test.shape
}

# Сохраняем в базу данных
storage_manager.save_pipeline_results(results)

print(" Результаты сохранены в базу данных SQLite")

# Проверяем сохраненные данные
print("\n Проверка сохраненных данных...")
db_path = PROJECT_ROOT / "ml_pipeline.db"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Проверяем таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f" Таблицы в БД: {[table[0] for table in tables]}")

# Проверяем последние записи
for table_name, in tables:
if table_name != 'sqlite_sequence':
cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
count = cursor.fetchone()[0]
print(f" Записей в {table_name}: {count}")

conn.close()

return True, results

except Exception as e:
print(f" Ошибка в пайплайне: {e}")
import traceback
traceback.print_exc()
return False, None

if __name__ == "__main__":
print(" ML Pipeline для диагностики рака молочной железы")
print("=" * 70)

success, results = run_full_pipeline()

if success:
print("\n Пайплайн успешно завершен!")
print("\n Сводка результатов:")
print(f" - Временная метка: {results['timestamp']}")
print(f" - Модель: {results['model_type']}")
print(f" - F1-score: {results['metrics']['f1_score']:.4f}")
print(f" - Accuracy: {results['metrics']['accuracy']:.4f}")
print(f" - Размер данных: {results['data_shape']}")
else:
print("\n Пайплайн завершился с ошибкой")
