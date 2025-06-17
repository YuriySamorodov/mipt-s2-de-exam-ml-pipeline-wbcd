"""
Модуль для загрузки и первичного анализа данных.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import os
import sys

# Добавляем корневую папку в путь для импорта конфигурации
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
from config.config_utils import Config, get_logger, ensure_dir
except ImportError:
# Fallback для случая, когда модуль запускается отдельно
import yaml
from dotenv import load_dotenv

def get_logger(name: str):
logging.basicConfig(level=logging.INFO)
return logging.getLogger(name)


logger = get_logger(__name__)


class DataLoader:
"""Класс для загрузки и первичного анализа данных Wisconsin Breast Cancer."""

def __init__(self, config: Optional[Config] = None):
"""
Инициализация загрузчика данных.

Args:
config: Объект конфигурации
"""
self.config = config or Config()
self.data_config = self.config.get_data_config()

def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
"""
Загружает данные из CSV файла.

Args:
file_path: Путь к файлу данных

Returns:
DataFrame с загруженными данными
"""
if file_path is None:
file_path = self.data_config.get("source_file", "data/wdbc.data.csv")

try:
logger.info(f"Загрузка данных из файла: {file_path}")

# Загружаем данные без заголовков
df = pd.read_csv(file_path, header=None)

# Присваиваем имена колонок
columns = self.data_config.get("columns", [])
if len(columns) == len(df.columns):
df.columns = columns
else:
logger.warning(f"Количество колонок в конфигурации ({len(columns)}) "
f"не совпадает с данными ({len(df.columns)})")
# Используем стандартные имена
df.columns = self._get_default_columns(len(df.columns))

logger.info(f"Данные успешно загружены. Размер: {df.shape}")
return df

except FileNotFoundError:
logger.error(f"Файл данных не найден: {file_path}")
raise
except Exception as e:
logger.error(f"Ошибка при загрузке данных: {str(e)}")
raise

def _get_default_columns(self, num_columns: int) -> list:
"""Возвращает стандартные имена колонок для Wisconsin Breast Cancer Dataset."""
base_columns = [
"id", "diagnosis",
"radius_mean", "texture_mean", "perimeter_mean", "area_mean",
"smoothness_mean", "compactness_mean", "concavity_mean",
"concave_points_mean", "symmetry_mean", "fractal_dimension_mean",
"radius_se", "texture_se", "perimeter_se", "area_se",
"smoothness_se", "compactness_se", "concavity_se",
"concave_points_se", "symmetry_se", "fractal_dimension_se",
"radius_worst", "texture_worst", "perimeter_worst", "area_worst",
"smoothness_worst", "compactness_worst", "concavity_worst",
"concave_points_worst", "symmetry_worst", "fractal_dimension_worst"
]

if num_columns <= len(base_columns):
return base_columns[:num_columns]
else:
# Добавляем дополнительные колонки если нужно
additional = [f"feature_{i}" for i in range(len(base_columns), num_columns)]
return base_columns + additional

def analyze_data(self, df: pd.DataFrame) -> dict:
"""
Выполняет первичный анализ данных.

Args:
df: DataFrame для анализа

Returns:
Словарь с результатами анализа
"""
logger.info("Начало первичного анализа данных")

analysis = {
"shape": df.shape,
"columns": list(df.columns),
"dtypes": df.dtypes.to_dict(),
"missing_values": df.isnull().sum().to_dict(),
"memory_usage": df.memory_usage(deep=True).sum(),
"duplicate_rows": df.duplicated().sum()
}

# Анализ целевой переменной (если есть колонка diagnosis)
if "diagnosis" in df.columns:
analysis["target_distribution"] = df["diagnosis"].value_counts().to_dict()
logger.info(f"Распределение целевой переменной: {analysis['target_distribution']}")

# Статистика для численных колонок
numeric_columns = df.select_dtypes(include=[np.number]).columns
if len(numeric_columns) > 0:
analysis["numeric_stats"] = df[numeric_columns].describe().to_dict()

logger.info(f"Анализ данных завершен. Найдено {analysis['missing_values']} пропущенных значений")
logger.info(f"Размер данных: {analysis['shape']}")
logger.info(f"Использование памяти: {analysis['memory_usage'] / 1024 / 1024:.2f} MB")

return analysis

def validate_data(self, df: pd.DataFrame) -> Tuple[bool, list]:
"""
Проверяет качество данных.

Args:
df: DataFrame для проверки

Returns:
Tuple (is_valid, list_of_issues)
"""
logger.info("Начало валидации данных")
issues = []

# Проверка на пустой датасет
if df.empty:
issues.append("Датасет пустой")

# Проверка обязательных колонок
required_columns = ["id", "diagnosis"]
missing_required = [col for col in required_columns if col not in df.columns]
if missing_required:
issues.append(f"Отсутствуют обязательные колонки: {missing_required}")

# Проверка на дубликаты ID
if "id" in df.columns:
duplicate_ids = df["id"].duplicated().sum()
if duplicate_ids > 0:
issues.append(f"Найдено {duplicate_ids} дублированных ID")

# Проверка целевой переменной
if "diagnosis" in df.columns:
unique_diagnoses = df["diagnosis"].unique()
valid_diagnoses = ["M", "B"] # Malignant, Benign
invalid_diagnoses = [d for d in unique_diagnoses if d not in valid_diagnoses]
if invalid_diagnoses:
issues.append(f"Неизвестные значения в diagnosis: {invalid_diagnoses}")

# Проверка на слишком много пропущенных значений
missing_threshold = 0.5 # 50%
high_missing_cols = []
for col in df.columns:
missing_ratio = df[col].isnull().sum() / len(df)
if missing_ratio > missing_threshold:
high_missing_cols.append(f"{col} ({missing_ratio:.2%})")

if high_missing_cols:
issues.append(f"Колонки с большим количеством пропусков: {high_missing_cols}")

is_valid = len(issues) == 0

if is_valid:
logger.info("Валидация данных прошла успешно")
else:
logger.warning(f"Найдены проблемы в данных: {issues}")

return is_valid, issues

def save_analysis_report(self, analysis: dict, output_path: str = "results/data_analysis.json"):
"""
Сохраняет отчет анализа данных.

Args:
analysis: Результаты анализа
output_path: Путь для сохранения отчета
"""
import json

ensure_dir(Path(output_path).parent)

# Конвертируем pandas dtypes в строки для JSON
if "dtypes" in analysis:
analysis["dtypes"] = {k: str(v) for k, v in analysis["dtypes"].items()}

try:
with open(output_path, 'w', encoding='utf-8') as f:
json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
logger.info(f"Отчет анализа сохранен: {output_path}")
except Exception as e:
logger.error(f"Ошибка при сохранении отчета: {str(e)}")
raise

def detect_data_drift(self, reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Dict[str, Any]:
"""
Обнаруживает дрейф данных между референсным и текущим датасетом.

Args:
reference_df: Референсный датасет
current_df: Текущий датасет

Returns:
Словарь с результатами анализа дрейфа
"""
logger.info("Анализ дрейфа данных")

drift_results = {
"statistical_drift": {},
"distribution_drift": {},
"summary": {"drift_detected": False, "affected_features": []}
}

# Получаем пересечение колонок
common_columns = set(reference_df.columns) & set(current_df.columns)
numeric_columns = [col for col in common_columns 
if reference_df[col].dtype in ['int64', 'float64'] and col != 'id']

for col in numeric_columns:
try:
# Статистический тест Колмогорова-Смирнова
from scipy.stats import ks_2samp
statistic, p_value = ks_2samp(reference_df[col].dropna(), current_df[col].dropna())

drift_results["statistical_drift"][col] = {
"ks_statistic": statistic,
"p_value": p_value,
"drift_detected": p_value < 0.05
}

# Сравнение статистик
ref_mean = reference_df[col].mean()
curr_mean = current_df[col].mean()
mean_diff = abs(curr_mean - ref_mean) / ref_mean if ref_mean != 0 else 0

drift_results["distribution_drift"][col] = {
"reference_mean": ref_mean,
"current_mean": curr_mean,
"mean_difference_pct": mean_diff * 100,
"significant_change": mean_diff > 0.1 # 10% порог
}

if drift_results["statistical_drift"][col]["drift_detected"]:
drift_results["summary"]["affected_features"].append(col)
drift_results["summary"]["drift_detected"] = True

except ImportError:
logger.warning(f"Scipy недоступен для анализа дрейфа колонки {col}")
except Exception as e:
logger.warning(f"Ошибка анализа дрейфа для {col}: {str(e)}")

logger.info(f"Анализ дрейфа завершен. Дрейф обнаружен в {len(drift_results['summary']['affected_features'])} признаках")
return drift_results

def generate_data_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
"""
Генерирует подробный отчет о качестве данных.

Args:
df: DataFrame для анализа

Returns:
Словарь с отчетом о качестве данных
"""
logger.info("Генерация отчета о качестве данных")

report = {
"basic_info": self.analyze_data(df),
"data_quality_issues": [],
"recommendations": [],
"quality_score": 0
}

# Проверка пропущенных значений
missing_pct = (df.isnull().sum() / len(df) * 100)
high_missing_cols = missing_pct[missing_pct > 5].to_dict()

if high_missing_cols:
report["data_quality_issues"].append({
"issue": "Высокий процент пропущенных значений",
"details": high_missing_cols,
"severity": "high" if max(high_missing_cols.values()) > 20 else "medium"
})
report["recommendations"].append("Рассмотреть стратегии заполнения пропущенных значений")

# Проверка дубликатов
duplicates = df.duplicated().sum()
if duplicates > 0:
report["data_quality_issues"].append({
"issue": "Дублированные записи",
"details": {"count": duplicates, "percentage": duplicates / len(df) * 100},
"severity": "medium" if duplicates / len(df) < 0.1 else "high"
})
report["recommendations"].append("Удалить или изучить дублированные записи")

# Проверка выбросов
numeric_cols = df.select_dtypes(include=[np.number]).columns
outlier_summary = {}

for col in numeric_cols:
if col != 'id':
q1 = df[col].quantile(0.25)
q3 = df[col].quantile(0.75)
iqr = q3 - q1
outliers = len(df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)])

if outliers > 0:
outlier_summary[col] = {
"count": outliers,
"percentage": outliers / len(df) * 100
}

if outlier_summary:
report["data_quality_issues"].append({
"issue": "Выбросы в данных",
"details": outlier_summary,
"severity": "low"
})
report["recommendations"].append("Проанализировать и обработать выбросы")

# Расчет общего балла качества
quality_score = 100
for issue in report["data_quality_issues"]:
if issue["severity"] == "high":
quality_score -= 30
elif issue["severity"] == "medium":
quality_score -= 20
elif issue["severity"] == "low":
quality_score -= 10

report["quality_score"] = max(0, quality_score)

logger.info(f"Отчет о качестве данных сгенерирован. Балл качества: {report['quality_score']}")
return report


def main():
"""Главная функция для тестирования модуля."""
try:
# Инициализация загрузчика
loader = DataLoader()

# Загрузка данных
df = loader.load_data()

# Анализ данных
analysis = loader.analyze_data(df)

# Валидация данных
is_valid, issues = loader.validate_data(df)

# Сохранение отчета
analysis["validation"] = {
"is_valid": is_valid,
"issues": issues
}
loader.save_analysis_report(analysis)

print(f"Загрузка и анализ данных завершены успешно!")
print(f"Размер данных: {df.shape}")
print(f"Валидность данных: {'Да' if is_valid else 'Нет'}")
if issues:
print(f"Проблемы: {issues}")

return df

except Exception as e:
logger.error(f"Ошибка в main: {str(e)}")
raise


if __name__ == "__main__":
main()
