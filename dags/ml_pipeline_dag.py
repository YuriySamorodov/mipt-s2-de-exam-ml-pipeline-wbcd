"""
DAG для автоматизации пайплайна машинного обучения.
Диагностика рака молочной железы на основе датасета Wisconsin Breast Cancer Diagnostic.
"""
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

# Добавляем путь к модулям ETL
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

def ensure_working_directory():
"""
Устанавливает рабочую директорию в корень проекта.
Эта функция должна вызываться в начале каждой задачи.
"""
import os
os.chdir(str(PROJECT_ROOT))
print(f"Рабочая директория установлена в: {os.getcwd()}")

# Импорты модулей ETL
try:
from src.etl.data_loader import DataLoader
from src.etl.data_preprocessor import DataPreprocessor
from src.etl.model_trainer import ModelTrainer
from src.etl.metrics_calculator import MetricsCalculator
from src.etl.storage_manager import StorageManager
from src.etl.data_quality_controller import DataQualityController
from config.config_utils import Config, get_logger
except ImportError as e:
print(f"Ошибка импорта модулей: {e}")
# Fallback imports для случая, когда модули не доступны
DataLoader = None
DataPreprocessor = None
ModelTrainer = None
MetricsCalculator = None
StorageManager = None
DataQualityController = None

# Настройка логирования
import logging
logger = logging.getLogger(__name__)

# Конфигурация DAG
DEFAULT_ARGS = {
'owner': 'data-engineer',
'depends_on_past': False,
'start_date': days_ago(1),
'email': ['admin@example.com'],
'email_on_failure': True,
'email_on_retry': False,
'retries': 2,
'retry_delay': timedelta(minutes=5),
'execution_timeout': timedelta(minutes=30),
}

# Создание DAG
dag = DAG(
'breast_cancer_ml_pipeline',
default_args=DEFAULT_ARGS,
description='Пайплайн машинного обучения для диагностики рака молочной железы',
schedule_interval=None, # Запуск по требованию
catchup=False,
max_active_runs=1,
tags=['machine-learning', 'healthcare', 'classification'],
)


def load_and_validate_data(**context):
"""
Задача загрузки и валидации данных с полной поддержкой XCom.
"""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

logger.info("=== НАЧАЛО ЗАГРУЗКИ И ВАЛИДАЦИИ ДАННЫХ ===")

try:
# Инициализируем загрузчик данных
loader = DataLoader()

# Загружаем данные
df = loader.load_data()
logger.info(f"Загружено записей: {len(df)}")

# Анализируем данные
analysis = loader.analyze_data(df)

# Валидируем данные
is_valid, issues = loader.validate_data(df)

if not is_valid:
error_msg = f"Данные не прошли валидацию: {issues}"
logger.error(error_msg)
raise ValueError(error_msg)

# Сохраняем отчет анализа
analysis["validation"] = {"is_valid": is_valid, "issues": issues}
loader.save_analysis_report(analysis)

# Подготавливаем данные для передачи через XCom
# Преобразуем DataFrame в сериализуемый формат
data_dict = {
'data': df.to_dict('records'), # Данные в формате списка словарей
'columns': df.columns.tolist(),
'dtypes': df.dtypes.astype(str).to_dict(),
'shape': df.shape,
'memory_usage': df.memory_usage(deep=True).sum()
}

# Передаем данные через XCom
context['task_instance'].xcom_push(key='raw_data', value=data_dict)
context['task_instance'].xcom_push(key='data_analysis', value=analysis)
context['task_instance'].xcom_push(key='validation_results', value={
'is_valid': is_valid, 
'issues': issues
})

logger.info(f" Данные успешно переданы через XCom (размер: {len(df)} записей)")
logger.info("=== ЗАГРУЗКА И ВАЛИДАЦИЯ ДАННЫХ ЗАВЕРШЕНЫ ===")

return {
"status": "success", 
"records": len(df), 
"columns": len(df.columns),
"memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
"issues": issues
}

except Exception as e:
logger.error(f"Ошибка в задаче загрузки данных: {str(e)}")
raise


def preprocess_data(**context):
"""
Задача предобработки данных с получением данных через XCom.
"""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

logger.info("=== НАЧАЛО ПРЕДОБРАБОТКИ ДАННЫХ ===")

try:
# Получаем данные из предыдущей задачи через XCom
raw_data_dict = context['task_instance'].xcom_pull(
task_ids='load_and_validate_data',
key='raw_data'
)

if raw_data_dict is None:
logger.warning("Не удалось получить данные через XCom, используем fallback загрузку")
# Fallback: загружаем данные напрямую
loader = DataLoader()
df = loader.load_data()
else:
# Восстанавливаем DataFrame из XCom данных
df = pd.DataFrame(raw_data_dict['data'])
df = df.astype(raw_data_dict['dtypes'])
logger.info(f" Получены данные через XCom: {df.shape}")

# Получаем дополнительную информацию
analysis = context['task_instance'].xcom_pull(
task_ids='load_and_validate_data',
key='data_analysis'
)

# Инициализируем препроцессор
preprocessor = DataPreprocessor()

# Выполняем полный пайплайн предобработки
X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df)

# Подготавливаем обработанные данные для передачи через XCom
processed_data = {
'X_train': X_train.tolist(), # Преобразуем numpy array в список
'X_test': X_test.tolist(),
'y_train': y_train.tolist(),
'y_test': y_test.tolist(),
'feature_names': X_train.columns.tolist() if hasattr(X_train, 'columns') else list(range(X_train.shape[1])),
'train_shape': X_train.shape,
'test_shape': X_test.shape,
}

# Передаем обработанные данные через XCom
context['task_instance'].xcom_push(key='processed_data', value=processed_data)
context['task_instance'].xcom_push(key='preprocessing_metadata', value={
'train_samples': len(y_train),
'test_samples': len(y_test),
'feature_count': X_train.shape[1],
'target_distribution': {
'train': {str(k): int(v) for k, v in pd.Series(y_train).value_counts().to_dict().items()},
'test': {str(k): int(v) for k, v in pd.Series(y_test).value_counts().to_dict().items()}
}
})

logger.info(f" Предобработанные данные переданы через XCom")
logger.info(f" - Обучающая выборка: {X_train.shape}")
logger.info(f" - Тестовая выборка: {X_test.shape}")
logger.info("=== ПРЕДОБРАБОТКА ДАННЫХ ЗАВЕРШЕНА ===")

return {
"status": "success",
"train_shape": X_train.shape,
"test_shape": X_test.shape,
"features": X_train.shape[1]
}

except Exception as e:
logger.error(f"Ошибка в задаче предобработки данных: {str(e)}")
raise


def train_model(**context):
"""
Задача обучения модели с получением данных через XCom.
"""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

logger.info("=== НАЧАЛО ОБУЧЕНИЯ МОДЕЛИ ===")

try:
# Получаем обработанные данные из XCom
processed_data = context['task_instance'].xcom_pull(
task_ids='preprocess_data',
key='processed_data'
)

if processed_data is None:
logger.warning("Данные не найдены в XCom, используем fallback подход")
# Fallback: загружаем и обрабатываем данные заново
loader = DataLoader()
df = loader.load_data()

preprocessor = DataPreprocessor()
X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df)
else:
# Восстанавливаем данные из XCom
X_train = np.array(processed_data['X_train'])
X_test = np.array(processed_data['X_test'])
y_train = np.array(processed_data['y_train'])
y_test = np.array(processed_data['y_test'])

logger.info(f" Получены обработанные данные через XCom:")
logger.info(f" - X_train: {X_train.shape}")
logger.info(f" - X_test: {X_test.shape}")
logger.info(f" - y_train: {len(y_train)} образцов")
logger.info(f" - y_test: {len(y_test)} образцов")

# Получаем метаданные предобработки
preprocessing_metadata = context['task_instance'].xcom_pull(
task_ids='preprocess_data',
key='preprocessing_metadata'
)

# Инициализируем тренера модели
trainer = ModelTrainer()

# Определяем, использовать ли подбор гиперпараметров
use_hyperparameter_tuning = Variable.get(
"use_hyperparameter_tuning", 
default_var=False, # Отключаем для стабильности
deserialize_json=True
)

# Обучаем модель
if processed_data is not None:
# Используем новый метод для XCom данных
training_results = trainer.train_model_from_data(
X_train, y_train,
use_hyperparameter_tuning=use_hyperparameter_tuning
)
else:
# Используем старый метод как fallback
training_results = trainer.train_full_pipeline(
X_train, y_train,
use_hyperparameter_tuning=use_hyperparameter_tuning
)

# Получаем обученную модель
trained_model = trainer.get_model()

# Подготавливаем данные модели для XCom (сериализуем параметры)
model_params = {}
if hasattr(trained_model, 'get_params'):
model_params = trained_model.get_params()

# Сохраняем модель в файл и передаем путь через XCom
model_path = "results/models/current_model.joblib"
trainer.save_model(model_path)

# Передаем результаты обучения через XCom
training_xcom_data = {
'model_path': model_path,
'model_type': type(trained_model).__name__,
'model_params': {k: str(v) for k, v in model_params.items()}, # Сериализуем параметры
'training_results': training_results,
'feature_count': X_train.shape[1],
'training_samples': len(y_train),
'hyperparameter_tuning_used': use_hyperparameter_tuning,
'cross_validation_score': training_results.get('baseline_cv', {}).get('mean_cv_score'),
'best_score': training_results.get('hyperparameter_tuning', {}).get('best_score'),
'data_source': 'xcom' if processed_data is not None else 'fallback'
}

context['task_instance'].xcom_push(key='training_results', value=training_xcom_data)
context['task_instance'].xcom_push(key='test_data', value={
'X_test': X_test.tolist(),
'y_test': y_test.tolist()
})

logger.info(f" Модель обучена и сохранена в {model_path}")
logger.info(f" - Тип модели: {type(trained_model).__name__}")
logger.info(f" - Источник данных: {'XCom' if processed_data is not None else 'Fallback'}")
logger.info(f" - Использован подбор гиперпараметров: {use_hyperparameter_tuning}")
logger.info("=== ОБУЧЕНИЕ МОДЕЛИ ЗАВЕРШЕНО ===")

return {
"status": "success",
"model_type": type(trained_model).__name__,
"model_path": model_path,
"training_samples": len(y_train),
"cv_score": training_results.get('baseline_cv', {}).get('mean_cv_score'),
"data_source": 'xcom' if processed_data is not None else 'fallback'
}

except Exception as e:
logger.error(f"Ошибка в задаче обучения модели: {str(e)}")
raise


def evaluate_model(**context):
"""
Задача оценки модели с получением модели и данных через XCom и fallback.
"""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

logger.info("=== НАЧАЛО ОЦЕНКИ МОДЕЛИ ===")

try:
# Получаем результаты обучения из XCom
training_data = context['task_instance'].xcom_pull(
task_ids='train_model',
key='training_results'
)

# Получаем тестовые данные из XCom
test_data = context['task_instance'].xcom_pull(
task_ids='train_model',
key='test_data'
)

if training_data is None or test_data is None:
logger.warning("Данные модели или тестовые данные не найдены в XCom, используем fallback подход")

# Fallback: воспроизводим весь пайплайн для получения модели и данных
loader = DataLoader()
df = loader.load_data()

preprocessor = DataPreprocessor()
X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df)

# Проверяем, есть ли сохраненная модель
model_path = "results/models/current_model.joblib"
if os.path.exists(model_path):
model = joblib.load(model_path)
logger.info(f" Загружена сохраненная модель: {model_path}")
else:
# Обучаем модель заново
trainer = ModelTrainer()
trainer.train_full_pipeline(X_train, y_train, use_hyperparameter_tuning=False)
trainer.save_model(model_path)
model = trainer.get_model()
logger.info(" Модель обучена заново")

# Используем fallback данные
X_test_final = X_test
y_test_final = y_test
model_type = type(model).__name__
data_source = 'fallback'

else:
# Восстанавливаем тестовые данные из XCom
X_test_final = np.array(test_data['X_test'])
y_test_final = np.array(test_data['y_test'])

logger.info(f" Получены данные через XCom:")
logger.info(f" - Путь к модели: {training_data['model_path']}")
logger.info(f" - Тестовые данные: {X_test_final.shape}")
logger.info(f" - Тип модели: {training_data['model_type']}")

# Загружаем обученную модель
model = joblib.load(training_data['model_path'])
model_type = training_data['model_type']
data_source = 'xcom'

# Оцениваем модель
calculator = MetricsCalculator()
metrics = calculator.evaluate_model(model, X_test_final, y_test_final)

# Сохраняем метрики
calculator.save_metrics(metrics)
calculator.generate_evaluation_report(metrics)

# Подготавливаем данные метрик для XCom
basic_metrics = metrics.get('basic_metrics', {})
probability_metrics = metrics.get('probability_metrics', {})

evaluation_xcom_data = {
'basic_metrics': basic_metrics,
'probability_metrics': probability_metrics,
'model_info': {
'model_type': model_type,
'model_path': training_data['model_path'] if training_data else "results/models/current_model.joblib",
'feature_count': X_test_final.shape[1],
'data_source': data_source
},
'test_info': {
'test_samples': len(y_test_final),
'test_shape': X_test_final.shape
},
'predictions_summary': {
'total_predictions': len(y_test_final),
'positive_predictions': int(np.sum(model.predict(X_test_final))),
'negative_predictions': int(len(y_test_final) - np.sum(model.predict(X_test_final)))
}
}

# Передаем метрики через XCom
context['task_instance'].xcom_push(key='evaluation_metrics', value=evaluation_xcom_data)

# Создаем краткую сводку для визуализации
metrics_summary = {
'accuracy': basic_metrics.get('accuracy', 0),
'precision': basic_metrics.get('precision', 0),
'recall': basic_metrics.get('recall', 0),
'f1_score': basic_metrics.get('f1_score', 0),
'roc_auc': probability_metrics.get('roc_auc', 0)
}

context['task_instance'].xcom_push(key='metrics_summary', value=metrics_summary)

logger.info(f" Модель оценена:")
logger.info(f" - Источник данных: {'XCom' if data_source == 'xcom' else 'Fallback'}")
logger.info(f" - Точность: {metrics_summary['accuracy']:.4f}")
logger.info(f" - Precision: {metrics_summary['precision']:.4f}")
logger.info(f" - Recall: {metrics_summary['recall']:.4f}")
logger.info(f" - F1-score: {metrics_summary['f1_score']:.4f}")
logger.info(f" - ROC AUC: {metrics_summary['roc_auc']:.4f}")
logger.info("=== ОЦЕНКА МОДЕЛИ ЗАВЕРШЕНА ===")

return {
"status": "success",
"accuracy": metrics_summary['accuracy'],
"f1_score": metrics_summary['f1_score'],
"roc_auc": metrics_summary['roc_auc'],
"data_source": data_source
}

except Exception as e:
logger.error(f"Ошибка в задаче оценки модели: {str(e)}")
raise


def save_results(**context):
"""
Задача сохранения результатов с полной интеграцией XCom.
Собирает все данные из предыдущих задач через XCom.
"""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

logger.info("=== НАЧАЛО СОХРАНЕНИЯ РЕЗУЛЬТАТОВ ===")

try:
# Инициализируем менеджер хранилища
logger.info("Инициализируем StorageManager...")
storage_manager = StorageManager()
logger.info("StorageManager инициализирован успешно")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Собираем все данные из XCom
logger.info("Собираем данные из XCom...")

# Данные загрузки
raw_data_info = context['task_instance'].xcom_pull(
task_ids='load_and_validate_data',
key='raw_data'
)
data_analysis = context['task_instance'].xcom_pull(
task_ids='load_and_validate_data',
key='data_analysis'
)
validation_results = context['task_instance'].xcom_pull(
task_ids='load_and_validate_data',
key='validation_results'
)

# Данные предобработки
processed_data_meta = context['task_instance'].xcom_pull(
task_ids='preprocess_data',
key='preprocessing_metadata'
)

# Данные обучения
training_results = context['task_instance'].xcom_pull(
task_ids='train_model',
key='training_results'
)

# Данные оценки
evaluation_metrics = context['task_instance'].xcom_pull(
task_ids='evaluate_model',
key='evaluation_metrics'
)
metrics_summary = context['task_instance'].xcom_pull(
task_ids='evaluate_model',
key='metrics_summary'
)

# Формируем полный отчет с XCom данными
complete_pipeline_results = {
"pipeline_execution": {
"dag_id": context['dag'].dag_id,
"run_id": context['dag_run'].run_id,
"logical_date": context['logical_date'].isoformat(),
"start_date": context['dag_run'].start_date.isoformat() if context['dag_run'].start_date else None,
"timestamp": timestamp,
"execution_mode": "XCom-based"
},
"data_summary": {
"original_shape": raw_data_info['shape'] if raw_data_info else None,
"original_columns": len(raw_data_info['columns']) if raw_data_info else None,
"memory_usage_mb": round(raw_data_info['memory_usage'] / 1024 / 1024, 2) if raw_data_info else None,
"validation_passed": validation_results['is_valid'] if validation_results else None,
"issues": validation_results['issues'] if validation_results else None
},
"preprocessing_summary": {
"train_samples": processed_data_meta['train_samples'] if processed_data_meta else None,
"test_samples": processed_data_meta['test_samples'] if processed_data_meta else None,
"feature_count": processed_data_meta['feature_count'] if processed_data_meta else None,
"target_distribution": processed_data_meta['target_distribution'] if processed_data_meta else None
},
"training_summary": {
"model_type": training_results['model_type'] if training_results else None,
"model_path": training_results['model_path'] if training_results else None,
"hyperparameter_tuning": training_results['hyperparameter_tuning_used'] if training_results else None,
"cv_score": training_results['cross_validation_score'] if training_results else None,
"best_score": training_results['best_score'] if training_results else None
},
"evaluation_summary": {
"basic_metrics": evaluation_metrics['basic_metrics'] if evaluation_metrics else None,
"probability_metrics": evaluation_metrics['probability_metrics'] if evaluation_metrics else None,
"test_samples": evaluation_metrics['test_info']['test_samples'] if evaluation_metrics else None,
"predictions_summary": evaluation_metrics['predictions_summary'] if evaluation_metrics else None
},
"key_metrics": metrics_summary if metrics_summary else {},
"data_analysis": data_analysis,
"xcom_data_integrity": {
"raw_data_available": raw_data_info is not None,
"preprocessing_available": processed_data_meta is not None,
"training_available": training_results is not None,
"evaluation_available": evaluation_metrics is not None,
"all_stages_complete": all([
raw_data_info is not None,
processed_data_meta is not None,
training_results is not None,
evaluation_metrics is not None
])
}
}

# Сохраняем полный отчет
results_path = f"results/complete_pipeline_results_{timestamp}.json"
success = storage_manager.save_to_local(complete_pipeline_results, results_path)

# Создаем список файлов для архивирования
files_to_archive = [results_path] if success else []

# Добавляем модель, если путь доступен из XCom
if training_results and training_results.get('model_path'):
model_path = training_results['model_path']
if os.path.exists(model_path):
files_to_archive.append(model_path)

# Проверяем другие файлы результатов
potential_files = [
"results/metrics.json",
"results/evaluation_report.md",
"results/confusion_matrix.png",
"results/roc_curve.png",
"results/precision_recall_curve.png"
]

for file_path in potential_files:
if os.path.exists(file_path):
files_to_archive.append(file_path)

# Создаем краткую сводку
save_summary = {
"timestamp": timestamp,
"execution_mode": "Full XCom Integration",
"total_files_saved": len(files_to_archive),
"files_list": files_to_archive,
"xcom_data_complete": complete_pipeline_results["xcom_data_integrity"]["all_stages_complete"],
"key_metrics": metrics_summary,
"pipeline_success": success
}

# Сохраняем сводку
summary_path = f"results/xcom_save_summary_{timestamp}.json"
storage_manager.save_to_local(save_summary, summary_path)

# Передаем результаты в XCom для возможного использования в следующих задачах
context['task_instance'].xcom_push(key='save_results_summary', value=save_summary)
context['task_instance'].xcom_push(key='complete_results_path', value=results_path)

logger.info(" Результаты успешно сохранены через XCom интеграцию:")
logger.info(f" - Полный отчет: {results_path}")
logger.info(f" - Файлов обработано: {len(files_to_archive)}")
logger.info(f" - XCom данные полные: {save_summary['xcom_data_complete']}")
if metrics_summary:
logger.info(f" - Точность модели: {metrics_summary.get('accuracy', 'N/A'):.4f}")
logger.info(f" - F1-score: {metrics_summary.get('f1_score', 'N/A'):.4f}")
logger.info("=== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ ЗАВЕРШЕНО ===")

return {
"status": "success",
"files_saved": len(files_to_archive),
"timestamp": timestamp,
"xcom_integration": True,
"results_path": results_path,
"data_complete": save_summary['xcom_data_complete']
}

except Exception as e:
logger.error(f"Ошибка в задаче сохранения результатов: {str(e)}")

# Сохраняем информацию об ошибке в XCom
error_info = {
"status": "error",
"error_message": str(e),
"timestamp": datetime.now().isoformat(),
"stage": "save_results"
}

try:
context['task_instance'].xcom_push(key='save_results_error', value=error_info)
except:
pass # Если XCom не работает, не падаем

return error_info


def cleanup_task(**context):
"""
Задача очистки временных файлов.
"""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

logger.info("=== НАЧАЛО ОЧИСТКИ ===")

try:
storage_manager = StorageManager()

# Очищаем старые результаты
max_age_days = int(Variable.get("cleanup_max_age_days", default_var=30))
deleted_count = storage_manager.cleanup_old_results(max_age_days=max_age_days)

logger.info(f"Очистка завершена. Удалено файлов: {deleted_count}")
logger.info("=== ОЧИСТКА ЗАВЕРШЕНА ===")

return {
"status": "success",
"deleted_files": deleted_count,
"max_age_days": max_age_days
}

except Exception as e:
logger.error(f"Ошибка в задаче очистки: {str(e)}")
raise


def data_quality_check(**context):
"""Проверка качества данных."""
# Устанавливаем рабочую директорию в корень проекта
ensure_working_directory()

try:
logger.info("Начало проверки качества данных")

# Загружаем данные заново (более надежный подход для Airflow)
loader = DataLoader()
df = loader.load_data()

if df is None or df.empty:
raise ValueError("Не удалось загрузить данные для проверки качества")

# Инициализируем контроллер качества
quality_controller = DataQualityController()

# Выполняем комплексную проверку качества
quality_results = quality_controller.run_comprehensive_checks(df, "wisconsin_dataset")

# Сохраняем отчет о качестве
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
quality_report_path = f"results/data_quality/quality_report_{timestamp}.json"
quality_controller.save_quality_report(quality_results, quality_report_path)

# Проверяем критические проблемы
if quality_results["overall_score"] < 60:
logger.warning(f"Низкий балл качества данных: {quality_results['overall_score']:.1f}")
logger.warning("Рассмотрите улучшение качества данных перед продолжением")

logger.info(f"Проверка качества завершена. Балл: {quality_results['overall_score']:.1f}")
return quality_results

except Exception as e:
logger.error(f"Ошибка при проверке качества данных: {str(e)}")
raise


# Определение задач DAG
task_load_data = PythonOperator(
task_id='load_and_validate_data',
python_callable=load_and_validate_data,
dag=dag,
doc_md="""
## Загрузка и валидация данных

Эта задача выполняет:
- Загрузку данных из файла Wisconsin Breast Cancer Diagnostic
- Первичный анализ данных (размер, типы, пропущенные значения)
- Валидацию качества данных
- Сохранение отчета анализа
""",
)

task_preprocess = PythonOperator(
task_id='preprocess_data',
python_callable=preprocess_data,
dag=dag,
doc_md="""
## Предобработка данных

Эта задача выполняет:
- Очистку данных (удаление дубликатов, обработка пропусков)
- Кодирование целевой переменной
- Разделение на обучающую и тестовую выборки
- Нормализацию признаков
- Сохранение препроцессоров
""",
)

task_train = PythonOperator(
task_id='train_model',
python_callable=train_model,
dag=dag,
doc_md="""
## Обучение модели

Эта задача выполняет:
- Создание модели логистической регрессии
- Кросс-валидацию с базовыми параметрами
- Подбор гиперпараметров (опционально)
- Финальное обучение модели
- Сохранение модели и метаданных
""",
)

task_evaluate = PythonOperator(
task_id='evaluate_model',
python_callable=evaluate_model,
dag=dag,
doc_md="""
## Оценка модели

Эта задача выполняет:
- Расчет основных метрик (accuracy, precision, recall, F1)
- Расчет вероятностных метрик (ROC AUC)
- Построение матрицы ошибок
- Создание визуализаций (ROC-кривая, Precision-Recall)
- Генерацию отчета об оценке
""",
)

task_save = PythonOperator(
task_id='save_results',
python_callable=save_results,
dag=dag,
doc_md="""
## Сохранение результатов

Эта задача выполняет:
- Сборку всех результатов пайплайна
- Создание архива с результатами
- Сохранение в локальное хранилище
- Загрузку в облачное хранилище (опционально)
""",
)

task_cleanup = PythonOperator(
task_id='cleanup',
python_callable=cleanup_task,
dag=dag,
trigger_rule='all_done', # Выполняется независимо от успеха предыдущих задач
doc_md="""
## Очистка

Эта задача выполняет:
- Удаление старых файлов результатов
- Освобождение дискового пространства
""",
)

task_quality_check = PythonOperator(
task_id='data_quality_check',
python_callable=data_quality_check,
dag=dag,
doc_md="""
## Проверка качества данных

Эта задача выполняет:
- Проверку качества загруженных данных
- Генерацию отчета о качестве данных
- Сохранение отчета в хранилище
""",
)

def health_check_task():
"""
Проверка системы и окружения.
Выполняется как Python функция для избежания zombie процессов.
"""
import os
import sys
import platform
from datetime import datetime

print("=== ПРОВЕРКА СИСТЕМЫ ===")
print(f"Дата и время: {datetime.now()}")
print(f"Пользователь: {os.getenv('USER', 'unknown')}")
print(f"Рабочая директория: {os.getcwd()}")
print(f"Версия Python: {sys.version}")
print(f"Платформа: {platform.system()} {platform.release()}")
print(f"Архитектура: {platform.machine()}")
print("=== ПРОВЕРКА ЗАВЕРШЕНА ===")

return {
"status": "success",
"timestamp": datetime.now().isoformat(),
"platform": platform.system(),
"python_version": sys.version.split()[0]
}

# Задача для проверки системы
task_health_check = PythonOperator(
task_id='health_check',
python_callable=health_check_task,
dag=dag,
)

# Определение зависимостей между задачами
task_health_check >> task_load_data >> task_preprocess >> task_train >> task_evaluate >> task_save >> task_cleanup
task_load_data >> task_quality_check

# Документация DAG
dag.doc_md = """
# Пайплайн машинного обучения для диагностики рака молочной железы

## Описание
Этот DAG автоматизирует полный цикл машинного обучения для бинарной классификации 
диагностики рака молочной железы на основе датасета Wisconsin Breast Cancer Diagnostic.

## Архитектура пайплайна
1. **health_check** - Проверка системы и окружения
2. **load_and_validate_data** - Загрузка и валидация данных
3. **preprocess_data** - Предобработка и подготовка данных
4. **train_model** - Обучение модели логистической регрессии
5. **evaluate_model** - Оценка модели и расчет метрик
6. **save_results** - Сохранение результатов в хранилище
7. **cleanup** - Очистка временных файлов
8. **data_quality_check** - Проверка качества данных

## Переменные Airflow
- `use_hyperparameter_tuning` (bool): Использовать ли подбор гиперпараметров
- `upload_to_cloud` (bool): Загружать ли результаты в облачное хранилище
- `cleanup_max_age_days` (int): Максимальный возраст файлов для очистки

## Выходные файлы
- Обученная модель: `results/models/current_model.joblib`
- Метрики: `results/metrics.json`
- Отчет оценки: `results/evaluation_report.md`
- Визуализации: `results/*.png`
- Архив результатов: `results/ml_pipeline_results_*.zip`
- Отчет о качестве данных: `results/data_quality/quality_report_*.json`

## Мониторинг и логирование
Все этапы пайплайна логируются с подробной информацией о процессе.
Результаты передаются между задачами через XCom.
"""
