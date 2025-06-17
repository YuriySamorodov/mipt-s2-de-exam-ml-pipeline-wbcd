#!/usr/bin/env python3
"""
Демонстраци print(" print(" print("\n3. Предобработка дан print("\n4. Обучение модели")ых print("\n5. Сохранение резул print("\n6. Сохра print("\n7. Мони print("\n8. Генераци print("\nДемонстрация завершена!") итогового отчета")оринг дрейфа данных") print("\n6. База данных недоступна")ение в базу данных")татов"))n2. Комплексная проверка качества данных")n1. Загрузка и первичный анализ данных") возможностей ETL пайплайна.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import os
import sys
import pandas as pd
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), ..)) # str(Path(__file__).parent))

from src.etl.data_loader import DataLoader
from src.etl.data_preprocessor import DataPreprocessor
from src.etl.model_trainer import ModelTrainer
from src.etl.data_quality_controller import DataQualityController
from src.etl.storage_manager import StorageManager
from config.config_utils import get_logger

logger = get_logger(__name__)


def demonstrate_etl():
"""Демонстрирует возможности ETL."""

print("Демонстрация ML Pipeline")
print("=" * 60)

# Инициализация компонентов
loader = DataLoader()
preprocessor = DataPreprocessor()
trainer = ModelTrainer()
quality_controller = DataQualityController()
storage_manager = StorageManager()

# 1. Загрузка и анализ данных
print("\n1. Загрузка и первичный анализ данных")
df = loader.load_data("data/wdbc.data.csv")
print(f" Загружено: {df.shape[0]} строк, {df.shape[1]} колонок")

# Генерация отчета о качестве данных
analysis = loader.analyze_data(df)
print(f" Пропущенные значения: {sum(analysis['missing_values'].values())}")
print(f" Дубликаты: {analysis['duplicate_rows']}")
print(f" Использование памяти: {analysis['memory_usage'] / 1024 / 1024:.2f} MB")

# 2. Комплексная проверка качества данных
print("\n2. Комплексная проверка качества данных")
quality_results = quality_controller.run_comprehensive_checks(df, "wisconsin_demo")
print(f" Общий балл качества: {quality_results['overall_score']:.1f}/100")
print(f" Уровень качества: {quality_results['quality_level'].upper()}")

# Сохранение отчета о качестве
quality_report_path = "results/demo_quality_report.json"
quality_controller.save_quality_report(quality_results, quality_report_path)
print(f" Отчет сохранен: {quality_report_path}")

# 3. Продвинутая предобработка данных
print("\n3. Предобработка данных")

# Очистка данных
df_clean = preprocessor.clean_data(df)
print(f" После очистки: {df_clean.shape[0]} строк")

# Обработка выбросов
df_no_outliers = preprocessor.handle_outliers(df_clean, method="cap", detection_method="iqr")
outliers_detected = preprocessor.detect_outliers(df_clean, method="iqr")
print(f" Обнаружено выбросов в {len(outliers_detected)} колонках")

# Feature Engineering
df_engineered = preprocessor.create_feature_engineering(df_no_outliers)
print(f" Создано новых признаков: {len(preprocessor.engineered_features)}")
print(f" Новые признаки: {', '.join(preprocessor.engineered_features[:5])}...")

# Подготовка признаков
df_prepared = preprocessor.prepare_features(df_engineered)
print(f" Подготовленные данные: {df_prepared.shape}")

# Разделение на X и y
target_column = "diagnosis_encoded" if "diagnosis_encoded" in df_prepared.columns else "diagnosis"
feature_columns = [col for col in df_prepared.columns if col not in ["diagnosis", "diagnosis_encoded"]]

X = df_prepared[feature_columns]
y = df_prepared[target_column]
print(f" Матрица признаков: {X.shape}")

# Отбор признаков
X_selected = preprocessor.select_features(X, y, method="univariate", n_features=15)
print(f" После отбора признаков: {X_selected.shape}")

# 4. Обучение модели с улучшениями
print("\n4. Обучение модели")

# Разделение данных
X_train, X_test, y_train, y_test = preprocessor.split_data(df_prepared)

# Используем отобранные признаки для обучения
X_train_selected = X_selected.loc[X_train.index]
X_test_selected = X_selected.loc[X_test.index]

# Нормализация данных
X_train_scaled, X_test_scaled = preprocessor.scale_features(X_train_selected, X_test_selected)

# Обучение модели
model = trainer.train_model(X_train_scaled, y_train)
print(f" Модель обучена: {type(model).__name__}")

# Предсказания
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

# Оценка модели
from src.etl.metrics_calculator import MetricsCalculator
metrics_calc = MetricsCalculator()
basic_metrics = metrics_calc.calculate_basic_metrics(y_test, y_pred)
prob_metrics = metrics_calc.calculate_probabilistic_metrics(y_test, y_pred_proba)

# Объединяем метрики
metrics = {**basic_metrics, **prob_metrics}

print(f" Точность: {metrics['accuracy']:.3f}")
print(f" Precision: {metrics['precision']:.3f}")
print(f" Recall: {metrics['recall']:.3f}")
print(f" F1-score: {metrics['f1_score']:.3f}")

# 5. Расширенное сохранение результатов
print("\n5. Сохранение результатов")

# Сохранение в локальное хранилище
import joblib
model_path = "results/models/demo_model.pkl"
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
success = os.path.exists(model_path)
print(f" Модель сохранена локально: {success}")

# Сохранение метрик
metrics_path = "results/metrics/demo_metrics.json"
storage_manager.save_to_local(metrics, metrics_path, "json")
print(f" Метрики сохранены: {metrics_path}")

# Создание архива результатов
import zipfile
archive_path = "results/demo_results.zip"
os.makedirs(os.path.dirname(archive_path), exist_ok=True)

with zipfile.ZipFile(archive_path, 'w') as zipf:
if os.path.exists(model_path):
zipf.write(model_path, os.path.basename(model_path))
if os.path.exists(metrics_path):
zipf.write(metrics_path, os.path.basename(metrics_path))
if os.path.exists(quality_report_path):
zipf.write(quality_report_path, os.path.basename(quality_report_path))

print(f" Создан архив: {archive_path}")

# Инициализация базы данных (если доступна)
if storage_manager.db_engine:
print("\n6. Сохранение в базу данных")

# Создание схемы
schema_created = storage_manager.create_tables_schema()
if schema_created:
print(" Схема БД создана успешно")

# Сохранение результатов эксперимента
experiment_saved = storage_manager.save_experiment_results(
"wisconsin_demo_experiment",
"LogisticRegression", 
model.get_params(),
{
"accuracy": float(metrics["accuracy"]),
"precision": float(metrics["precision"]),
"recall": float(metrics["recall"]),
"f1_score": float(metrics["f1_score"])
}
)

if experiment_saved:
print(" Эксперимент сохранен в БД")
else:
print(" Ошибка сохранения в БД")
else:
print("\n6. База данных недоступна")

# 7. Демонстрация мониторинга дрейфа данных
print("\n7. Мониторинг дрейфа данных")

# Создаем "новые" данные (симулируем изменения)
df_new = df.copy()
# Добавляем небольшие изменения
numeric_cols = df_new.select_dtypes(include=['float64', 'int64']).columns
for col in numeric_cols[:3]: # Изменяем первые 3 колонки
if col != 'id':
df_new[col] = df_new[col] * 1.1 # Увеличиваем на 10%

# Проверяем дрейф
drift_results = loader.detect_data_drift(df, df_new)
affected_features = drift_results["summary"]["affected_features"]

print(f" Дрейф обнаружен: {drift_results['summary']['drift_detected']}")
print(f" Затронутые признаки: {len(affected_features)}")
if affected_features:
print(f" Примеры: {', '.join(affected_features[:3])}")

# 8. Генерация итогового отчета
print("\n8. Генерация итогового отчета")

detailed_report = loader.generate_data_quality_report(df)
print(f" Общий балл качества: {detailed_report['quality_score']}")
print(f" Обнаружено проблем: {len(detailed_report['data_quality_issues'])}")
print(f" Рекомендации: {len(detailed_report['recommendations'])}")

# Сохранение полного отчета
full_report = {
"data_quality": quality_results,
"model_metrics": metrics,
"feature_engineering": {
"original_features": X.shape[1],
"engineered_features": len(preprocessor.engineered_features),
"selected_features": X_selected.shape[1]
},
"drift_analysis": drift_results,
"detailed_analysis": detailed_report
}

report_path = "results/comprehensive_demo_report.json"
storage_manager.save_to_local(full_report, report_path, "json")
print(f" Полный отчет сохранен: {report_path}")

print("\nДемонстрация завершена!")
print("=" * 60)
print("Основные возможности продемонстрированы:")
print(" • Комплексный контроль качества данных")
print(" • Продвинутая обработка выбросов")
print(" • Автоматическое создание признаков")
print(" • Интеллектуальный отбор признаков")
print(" • Интеграция с базами данных")
print(" • Мониторинг дрейфа данных")
print(" • Расширенные возможности хранения")


if __name__ == "__main__":
try:
demonstrate_etl()
except Exception as e:
logger.error(f"Ошибка демонстрации: {str(e)}")
raise
