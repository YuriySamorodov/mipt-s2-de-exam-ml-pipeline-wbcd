#!/usr/bin/env python3
"""
Простой скрипт для запуска ML пайплайна без Airflow
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ..)) # os.path.dirname(os.path.abspath(__file__)))

from src.etl.data_loader import DataLoader
from src.etl.data_preprocessor import DataPreprocessor
from src.etl.model_trainer import ModelTrainer
from src.etl.metrics_calculator import MetricsCalculator
from src.etl.storage_manager import StorageManager
from src.etl.data_quality_controller import DataQualityController

def run_ml_pipeline():
"""Запуск полного ML пайплайна"""
print(" Запуск ML пайплайна...")

try:
# 1. Загрузка данных
print("\n Шаг 1: Загрузка данных...")
data_loader = DataLoader()
data = data_loader.load_data()
print(f" Данные загружены: {data.shape}")

# 2. Контроль качества данных
print("\n Шаг 2: Контроль качества данных...")
quality_controller = DataQualityController()
quality_report = quality_controller.run_comprehensive_checks(data)
print(f" Контроль качества выполнен")

# 3. Предобработка данных
print("\n Шаг 3: Предобработка данных...")
preprocessor = DataPreprocessor()
X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(data)
print(f" Данные предобработаны: train={X_train.shape}, test={X_test.shape}")

# 4. Обучение модели
print("\n Шаг 4: Обучение модели...")
trainer = ModelTrainer()
model = trainer.train_model(X_train, y_train)
predictions = model.predict(X_test)
print(f" Модель обучена и сделаны предсказания")

# 5. Расчет метрик
print("\n Шаг 5: Расчет метрик...")
metrics_calc = MetricsCalculator()
metrics = metrics_calc.calculate_metrics(y_test, predictions)
print(f" Метрики рассчитаны: accuracy={metrics['accuracy']:.3f}")

# 6. Сохранение результатов
print("\n Шаг 6: Сохранение результатов...")
storage = StorageManager()
save_summary = storage.save_results(
model=model,
metrics=metrics,
data_summary={"shape": data.shape, "features": list(data.columns)},
quality_report=quality_report
)
print(f" Результаты сохранены: {save_summary}")

print("\n ML пайплайн успешно завершен!")
return True

except Exception as e:
print(f" Ошибка в ML пайплайне: {e}")
return False

if __name__ == "__main__":
success = run_ml_pipeline()
sys.exit(0 if success else 1)
