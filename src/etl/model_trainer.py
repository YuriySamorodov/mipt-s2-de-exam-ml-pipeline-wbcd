"""
Модуль для обучения модели машинного обучения.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import numpy as np
import pandas as pd
import logging
from typing import Tuple, Dict, Any, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV
import joblib
import json
from datetime import datetime
import os
import sys

# Добавляем корневую папку в путь для импорта конфигурации
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
from config.config_utils import Config, get_logger, ensure_dir
except ImportError:
def get_logger(name: str):
logging.basicConfig(level=logging.INFO)
return logging.getLogger(name)


logger = get_logger(__name__)


class ModelTrainer:
"""Класс для обучения модели логистической регрессии."""

def __init__(self, config: Optional[Config] = None):
"""
Инициализация тренера модели.

Args:
config: Объект конфигурации
"""
self.config = config or Config()
self.model_config = self.config.get_model_config()
self.model = None
self.training_history = {}
self.best_params = {}

def create_model(self) -> LogisticRegression:
"""
Создает модель логистической регрессии с параметрами из конфигурации.

Returns:
Инициализированная модель
"""
model_params = self.model_config.get("parameters", {})

# Параметры по умолчанию
default_params = {
"random_state": 42,
"max_iter": 1000,
"solver": "liblinear", # liblinear поддерживает l1 и l2
"penalty": "l2" # l2 по умолчанию
}

# Объединяем параметры
final_params = {**default_params, **model_params}

logger.info(f"Создание модели LogisticRegression с параметрами: {final_params}")

self.model = LogisticRegression(**final_params)
return self.model

def train_model(self, X_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression:
"""
Обучает модель на обучающих данных.

Args:
X_train: Обучающие признаки
y_train: Обучающие метки

Returns:
Обученная модель
"""
logger.info("Начало обучения модели")

if self.model is None:
self.create_model()

# Записываем время начала обучения
start_time = datetime.now()

# Обучаем модель
self.model.fit(X_train, y_train)

# Записываем время окончания
end_time = datetime.now()
training_time = (end_time - start_time).total_seconds()

# Сохраняем информацию об обучении
self.training_history = {
"start_time": start_time.isoformat(),
"end_time": end_time.isoformat(),
"training_time_seconds": training_time,
"training_samples": len(X_train),
"features_count": X_train.shape[1],
"model_params": self.model.get_params()
}

logger.info(f"Обучение завершено за {training_time:.2f} секунд")
logger.info(f"Обучено на {len(X_train)} образцах с {X_train.shape[1]} признаками")

return self.model

def hyperparameter_tuning(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
"""
Выполняет подбор гиперпараметров с помощью Grid Search.

Args:
X_train: Обучающие признаки
y_train: Обучающие метки

Returns:
Словарь с лучшими параметрами
"""
logger.info("Начало подбора гиперпараметров")

# Определяем сетку параметров для поиска
# Создаем совместимые комбинации solver и penalty
param_grid = [
# liblinear поддерживает l1 и l2
{
'C': [0.01, 0.1, 1, 10, 100],
'solver': ['liblinear'],
'penalty': ['l1', 'l2'],
'max_iter': [1000, 2000]
},
# lbfgs поддерживает только l2 и none
{
'C': [0.01, 0.1, 1, 10, 100],
'solver': ['lbfgs'],
'penalty': ['l2'],
'max_iter': [1000, 2000]
}
]

# Создаем базовую модель
base_model = LogisticRegression(random_state=42)

# Настраиваем GridSearchCV
grid_search = GridSearchCV(
estimator=base_model,
param_grid=param_grid,
cv=5, # 5-fold cross-validation
scoring='accuracy',
n_jobs=-1, # Используем все доступные ядра
verbose=1
)

# Выполняем поиск
start_time = datetime.now()
grid_search.fit(X_train, y_train)
end_time = datetime.now()

search_time = (end_time - start_time).total_seconds()

# Сохраняем результаты
self.best_params = grid_search.best_params_

tuning_results = {
"best_params": grid_search.best_params_,
"best_score": grid_search.best_score_,
"search_time_seconds": search_time,
"cv_results": {
"mean_test_scores": grid_search.cv_results_['mean_test_score'].tolist(),
"std_test_scores": grid_search.cv_results_['std_test_score'].tolist(),
"params": grid_search.cv_results_['params']
}
}

logger.info(f"Подбор гиперпараметров завершен за {search_time:.2f} секунд")
logger.info(f"Лучшие параметры: {self.best_params}")
logger.info(f"Лучший результат CV: {grid_search.best_score_:.4f}")

# Обновляем модель с лучшими параметрами
self.model = grid_search.best_estimator_

return tuning_results

def cross_validate_model(self, X_train: np.ndarray, y_train: np.ndarray, cv: int = 5) -> Dict[str, float]:
"""
Выполняет кросс-валидацию модели.

Args:
X_train: Обучающие признаки
y_train: Обучающие метки
cv: Количество фолдов для кросс-валидации

Returns:
Словарь с результатами кросс-валидации
"""
logger.info(f"Начало кросс-валидации с {cv} фолдами")

if self.model is None:
self.create_model()

# Выполняем кросс-валидацию
cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv, scoring='accuracy')

cv_results = {
"cv_scores": cv_scores.tolist(),
"mean_cv_score": float(cv_scores.mean()),
"std_cv_score": float(cv_scores.std()),
"min_cv_score": float(cv_scores.min()),
"max_cv_score": float(cv_scores.max())
}

logger.info(f"Результаты кросс-валидации:")
logger.info(f" Средняя точность: {cv_results['mean_cv_score']:.4f} ± {cv_results['std_cv_score']:.4f}")
logger.info(f" Минимальная точность: {cv_results['min_cv_score']:.4f}")
logger.info(f" Максимальная точность: {cv_results['max_cv_score']:.4f}")

return cv_results

def get_feature_importance(self, feature_names: list = None) -> Dict[str, float]:
"""
Получает важность признаков для модели.

Args:
feature_names: Названия признаков

Returns:
Словарь с важностью признаков
"""
if self.model is None:
logger.warning("Модель не обучена. Невозможно получить важность признаков.")
return {}

# Для логистической регрессии используем коэффициенты
coefficients = self.model.coef_[0]

if feature_names is None:
feature_names = [f"feature_{i}" for i in range(len(coefficients))]

# Создаем словарь важности (по абсолютному значению коэффициентов)
importance_dict = {
name: float(abs(coef)) 
for name, coef in zip(feature_names, coefficients)
}

# Сортируем по важности
importance_dict = dict(sorted(importance_dict.items(), 
key=lambda x: x[1], reverse=True))

logger.info(f"Топ-5 самых важных признаков:")
for i, (feature, importance) in enumerate(list(importance_dict.items())[:5]):
logger.info(f" {i+1}. {feature}: {importance:.4f}")

return importance_dict

def save_model(self, model_path: str = None):
"""
Сохраняет обученную модель и метаданные.

Args:
model_path: Полный путь к файлу модели. Если None, используется стандартная директория.
"""
if self.model is None:
logger.error("Модель не обучена. Нечего сохранять.")
return

try:
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if model_path is None:
# Используем стандартную директорию
output_dir = "results/models/"
ensure_dir(output_dir)
model_path = os.path.join(output_dir, f"logistic_regression_model_{timestamp}.joblib")
current_model_path = os.path.join(output_dir, "current_model.joblib")
else:
# Используем указанный путь
output_dir = os.path.dirname(model_path)
ensure_dir(output_dir)
current_model_path = model_path

# Удаляем существующий файл, если он есть
if os.path.exists(current_model_path):
os.remove(current_model_path)
logger.info(f"Удален существующий файл модели: {current_model_path}")

# Сохраняем модель
joblib.dump(self.model, current_model_path)
logger.info(f"Модель сохранена: {current_model_path}")

# Если используется стандартная директория, сохраняем также с timestamp
if model_path is None:
timestamped_path = os.path.join(output_dir, f"logistic_regression_model_{timestamp}.joblib")
joblib.dump(self.model, timestamped_path)
logger.info(f"Архивная копия модели сохранена: {timestamped_path}")

# Сохраняем метаданные
metadata = {
"model_type": "LogisticRegression",
"timestamp": timestamp,
"training_history": self.training_history,
"best_params": self.best_params,
"model_params": self.model.get_params() if self.model else {}
}

metadata_path = current_model_path.replace(".joblib", "_metadata.json")
with open(metadata_path, 'w', encoding='utf-8') as f:
json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
logger.info(f"Метаданные модели сохранены: {metadata_path}")

except Exception as e:
logger.error(f"Ошибка при сохранении модели: {str(e)}")
raise

# Сохраняем текущие метаданные
current_metadata_path = os.path.join(output_dir, "current_model_metadata.json")
with open(current_metadata_path, 'w', encoding='utf-8') as f:
json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

except Exception as e:
logger.error(f"Ошибка при сохранении модели: {str(e)}")
raise

def load_model(self, model_path: str = "results/models/current_model.joblib"):
"""
Загружает сохраненную модель.

Args:
model_path: Путь к файлу модели
"""
try:
if os.path.exists(model_path):
self.model = joblib.load(model_path)
logger.info(f"Модель загружена: {model_path}")

# Пытаемся загрузить метаданные
metadata_path = model_path.replace(".joblib", "_metadata.json")
if not os.path.exists(metadata_path):
metadata_path = os.path.join(os.path.dirname(model_path), "current_model_metadata.json")

if os.path.exists(metadata_path):
with open(metadata_path, 'r', encoding='utf-8') as f:
metadata = json.load(f)
self.training_history = metadata.get("training_history", {})
self.best_params = metadata.get("best_params", {})
logger.info("Метаданные модели загружены")
else:
logger.error(f"Файл модели не найден: {model_path}")

except Exception as e:
logger.error(f"Ошибка при загрузке модели: {str(e)}")
raise

def train_full_pipeline(self, X_train: np.ndarray, y_train: np.ndarray, 
use_hyperparameter_tuning: bool = True) -> Dict[str, Any]:
"""
Полный пайплайн обучения модели.

Args:
X_train: Обучающие признаки
y_train: Обучающие метки
use_hyperparameter_tuning: Использовать ли подбор гиперпараметров

Returns:
Словарь с результатами обучения
"""
logger.info("Запуск полного пайплайна обучения")

results = {}

# 1. Кросс-валидация с базовыми параметрами
self.create_model()
cv_results = self.cross_validate_model(X_train, y_train)
results["baseline_cv"] = cv_results

# 2. Подбор гиперпараметров (если требуется)
if use_hyperparameter_tuning:
tuning_results = self.hyperparameter_tuning(X_train, y_train)
results["hyperparameter_tuning"] = tuning_results

# 3. Финальное обучение модели
self.train_model(X_train, y_train)

# 4. Получение важности признаков
feature_importance = self.get_feature_importance()
results["feature_importance"] = feature_importance

# 5. Сохранение модели
self.save_model()

logger.info("Полный пайплайн обучения завершен успешно")

return results

def train_model_from_data(self, X_train: np.ndarray, y_train: np.ndarray, 
use_hyperparameter_tuning: bool = True) -> Dict[str, Any]:
"""
Обучение модели на предоставленных данных (для XCom интеграции).

Args:
X_train: Обучающие признаки
y_train: Обучающие метки
use_hyperparameter_tuning: Использовать ли подбор гиперпараметров

Returns:
Словарь с результатами обучения
"""
logger.info("Запуск обучения модели на данных из XCom")

results = {}

# 1. Кросс-валидация с базовыми параметрами
self.create_model()
cv_results = self.cross_validate_model(X_train, y_train)
results["baseline_cv"] = cv_results

# 2. Подбор гиперпараметров (если требуется)
if use_hyperparameter_tuning:
tuning_results = self.hyperparameter_tuning(X_train, y_train)
results["hyperparameter_tuning"] = tuning_results

# 3. Финальное обучение модели
self.train_model(X_train, y_train)

# 4. Получение важности признаков
feature_importance = self.get_feature_importance()
results["feature_importance"] = feature_importance

logger.info("Обучение модели на XCom данных завершено успешно")

return results

def get_model(self):
"""Возвращает обученную модель."""
return self.model


def main():
"""Главная функция для тестирования модуля."""
try:
# Импортируем модули предобработки
from data_loader import DataLoader
from data_preprocessor import DataPreprocessor

# Загружаем и предобрабатываем данные
loader = DataLoader()
df = loader.load_data()

preprocessor = DataPreprocessor()
X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df)

# Инициализируем и обучаем модель
trainer = ModelTrainer()

# Запускаем полный пайплайн обучения
results = trainer.train_full_pipeline(X_train, y_train, use_hyperparameter_tuning=True)

print(f"Обучение модели завершено успешно!")
if "baseline_cv" in results:
print(f"Baseline CV точность: {results['baseline_cv']['mean_cv_score']:.4f}")
if "hyperparameter_tuning" in results:
print(f"Лучшая CV точность: {results['hyperparameter_tuning']['best_score']:.4f}")

return trainer.model, results

except Exception as e:
logger.error(f"Ошибка в main: {str(e)}")
raise


if __name__ == "__main__":
main()
