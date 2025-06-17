"""
Модуль для контроля качества данных (Data Quality).

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import hashlib
import json
import os
import sys

# Добавляем корневую папку в путь для импорта конфигурации
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
from config.config_utils import Config, get_logger
except ImportError:
def get_logger(name: str):
logging.basicConfig(level=logging.INFO)
return logging.getLogger(name)

logger = get_logger(__name__)


class DataQualityController:
"""Класс для контроля качества данных."""

def __init__(self, config: Optional[Config] = None):
"""
Инициализация контроллера качества данных.

Args:
config: Объект конфигурации
"""
self.config = config or Config()
self.quality_config = self.config.config.get("data_quality", {})
self.thresholds = self.quality_config.get("thresholds", {})
self.drift_config = self.quality_config.get("drift_detection", {})

# История проверок качества
self.quality_history = []

def run_comprehensive_checks(self, df: pd.DataFrame, 
dataset_name: str = "current") -> Dict[str, Any]:
"""
Запускает комплексную проверку качества данных.

Args:
df: DataFrame для проверки
dataset_name: Название датасета

Returns:
Результаты всех проверок качества
"""
logger.info(f"Запуск комплексной проверки качества для {dataset_name}")

results = {
"dataset_name": dataset_name,
"timestamp": datetime.now().isoformat(),
"data_hash": self._calculate_data_hash(df),
"basic_statistics": self._get_basic_statistics(df),
"missing_values": self._check_missing_values(df),
"duplicates": self._check_duplicates(df),
"outliers": self._detect_outliers(df),
"data_types": self._validate_data_types(df),
"value_ranges": self._check_value_ranges(df),
"consistency": self._check_data_consistency(df),
"completeness": self._check_completeness(df),
"validity": self._check_validity(df),
"overall_score": 0
}

# Расчет общего балла качества
results["overall_score"] = self._calculate_quality_score(results)
results["quality_level"] = self._get_quality_level(results["overall_score"])

# Сохранение в историю
self.quality_history.append(results)

logger.info(f"Проверка качества завершена. Балл: {results['overall_score']:.1f}")
return results

def _calculate_data_hash(self, df: pd.DataFrame) -> str:
"""Вычисляет хэш данных для отслеживания изменений."""
data_string = df.to_string().encode('utf-8')
return hashlib.sha256(data_string).hexdigest()[:16]

def _get_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Получает базовую статистику датасета."""
return {
"shape": df.shape,
"memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
"column_count": len(df.columns),
"row_count": len(df),
"numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
"categorical_columns": len(df.select_dtypes(include=['object', 'category']).columns)
}

def _check_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет пропущенные значения."""
missing_stats = df.isnull().sum()
missing_pct = (missing_stats / len(df) * 100).round(2)

threshold = self.thresholds.get("missing_values_pct", 5.0)
problematic_columns = missing_pct[missing_pct > threshold].to_dict()

return {
"total_missing": int(missing_stats.sum()),
"missing_by_column": missing_stats.to_dict(),
"missing_percentage": missing_pct.to_dict(),
"problematic_columns": problematic_columns,
"threshold_exceeded": len(problematic_columns) > 0,
"severity": "high" if len(problematic_columns) > 0 else "low"
}

def _check_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет дублированные записи."""
duplicates_count = df.duplicated().sum()
duplicates_pct = (duplicates_count / len(df) * 100) if len(df) > 0 else 0

threshold = self.thresholds.get("duplicate_rows_pct", 1.0)

return {
"duplicate_count": int(duplicates_count),
"duplicate_percentage": round(duplicates_pct, 2),
"threshold_exceeded": duplicates_pct > threshold,
"severity": "high" if duplicates_pct > threshold else "low"
}

def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Обнаруживает выбросы в данных."""
numeric_columns = df.select_dtypes(include=[np.number]).columns
numeric_columns = [col for col in numeric_columns if col != 'id']

outliers_summary = {}
total_outliers = 0

for col in numeric_columns:
q1 = df[col].quantile(0.25)
q3 = df[col].quantile(0.75)
iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
outliers_count = len(outliers)
outliers_pct = (outliers_count / len(df) * 100) if len(df) > 0 else 0

if outliers_count > 0:
outliers_summary[col] = {
"count": outliers_count,
"percentage": round(outliers_pct, 2),
"lower_bound": lower_bound,
"upper_bound": upper_bound
}
total_outliers += outliers_count

threshold = self.thresholds.get("outliers_pct", 10.0)
total_outliers_pct = (total_outliers / len(df) / len(numeric_columns) * 100) if len(numeric_columns) > 0 else 0

return {
"outliers_by_column": outliers_summary,
"total_outliers": total_outliers,
"outliers_percentage": round(total_outliers_pct, 2),
"threshold_exceeded": total_outliers_pct > threshold,
"severity": "medium" if total_outliers_pct > threshold else "low"
}

def _validate_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет соответствие типов данных."""
type_issues = []

# Проверяем колонку diagnosis
if 'diagnosis' in df.columns:
valid_values = {'M', 'B'}
invalid_diagnosis = set(df['diagnosis'].unique()) - valid_values
if invalid_diagnosis:
type_issues.append({
"column": "diagnosis",
"issue": "Invalid values",
"details": list(invalid_diagnosis)
})

# Проверяем, что числовые колонки действительно числовые
for col in df.columns:
if col not in ['id', 'diagnosis']:
if not pd.api.types.is_numeric_dtype(df[col]):
type_issues.append({
"column": col,
"issue": "Expected numeric type",
"current_type": str(df[col].dtype)
})

return {
"type_issues": type_issues,
"issues_found": len(type_issues) > 0,
"severity": "high" if len(type_issues) > 0 else "low"
}

def _check_value_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет разумность диапазонов значений."""
range_issues = []
numeric_columns = df.select_dtypes(include=[np.number]).columns

for col in numeric_columns:
if col != 'id':
col_min = df[col].min()
col_max = df[col].max()

# Проверяем на отрицательные значения (для медицинских данных обычно положительные)
if col_min < 0:
range_issues.append({
"column": col,
"issue": "Negative values found",
"min_value": col_min
})

# Проверяем на экстремально большие значения
if col_max > 10000: # Примерный порог
range_issues.append({
"column": col,
"issue": "Extremely large values",
"max_value": col_max
})

return {
"range_issues": range_issues,
"issues_found": len(range_issues) > 0,
"severity": "medium" if len(range_issues) > 0 else "low"
}

def _check_data_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет согласованность данных."""
consistency_issues = []

# Проверяем уникальность ID
if 'id' in df.columns:
duplicate_ids = df['id'].duplicated().sum()
if duplicate_ids > 0:
consistency_issues.append({
"issue": "Duplicate IDs found",
"count": duplicate_ids
})

# Проверяем соответствие связанных признаков (например, radius и area)
if all(col in df.columns for col in ['radius_mean', 'area_mean']):
# Проверяем физическую согласованность (площадь должна расти с радиусом)
correlation = df['radius_mean'].corr(df['area_mean'])
if correlation < 0.5: # Ожидаем сильную положительную корреляцию
consistency_issues.append({
"issue": "Weak correlation between radius and area",
"correlation": correlation
})

return {
"consistency_issues": consistency_issues,
"issues_found": len(consistency_issues) > 0,
"severity": "high" if len(consistency_issues) > 0 else "low"
}

def _check_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет полноту данных."""
expected_columns = [
'id', 'diagnosis', 'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean'
]

missing_columns = [col for col in expected_columns if col not in df.columns]
extra_columns = [col for col in df.columns if col not in expected_columns and not any(
expected in col for expected in ['mean', 'se', 'worst']
)]

return {
"missing_columns": missing_columns,
"extra_columns": extra_columns,
"completeness_score": (len(expected_columns) - len(missing_columns)) / len(expected_columns),
"issues_found": len(missing_columns) > 0,
"severity": "high" if len(missing_columns) > 0 else "low"
}

def _check_validity(self, df: pd.DataFrame) -> Dict[str, Any]:
"""Проверяет валидность данных согласно бизнес-правилам."""
validity_issues = []

# Проверяем, что есть оба класса в целевой переменной
if 'diagnosis' in df.columns:
unique_diagnoses = df['diagnosis'].unique()
if len(unique_diagnoses) < 2:
validity_issues.append({
"issue": "Target variable has less than 2 classes",
"unique_values": list(unique_diagnoses)
})

# Проверяем минимальный размер выборки
min_sample_size = 100 # Минимум для ML
if len(df) < min_sample_size:
validity_issues.append({
"issue": "Dataset too small for reliable ML",
"current_size": len(df),
"minimum_required": min_sample_size
})

return {
"validity_issues": validity_issues,
"issues_found": len(validity_issues) > 0,
"severity": "high" if len(validity_issues) > 0 else "low"
}

def _calculate_quality_score(self, results: Dict[str, Any]) -> float:
"""Вычисляет общий балл качества данных."""
score = 100.0

# Штрафы за различные проблемы
penalties = {
"missing_values": 20 if results["missing_values"]["threshold_exceeded"] else 0,
"duplicates": 15 if results["duplicates"]["threshold_exceeded"] else 0,
"outliers": 10 if results["outliers"]["threshold_exceeded"] else 0,
"data_types": 25 if results["data_types"]["issues_found"] else 0,
"value_ranges": 15 if results["value_ranges"]["issues_found"] else 0,
"consistency": 20 if results["consistency"]["issues_found"] else 0,
"completeness": 30 if results["completeness"]["issues_found"] else 0,
"validity": 25 if results["validity"]["issues_found"] else 0
}

total_penalty = sum(penalties.values())
return max(0.0, score - total_penalty)

def _get_quality_level(self, score: float) -> str:
"""Определяет уровень качества данных по баллу."""
if score >= 90:
return "excellent"
elif score >= 80:
return "good"
elif score >= 70:
return "acceptable"
elif score >= 60:
return "poor"
else:
return "critical"

def generate_quality_report(self, results: Dict[str, Any]) -> str:
"""
Генерирует текстовый отчет о качестве данных.

Args:
results: Результаты проверки качества

Returns:
Текстовый отчет
"""
report_lines = [
f"=== ОТЧЕТ О КАЧЕСТВЕ ДАННЫХ ===",
f"Датасет: {results['dataset_name']}",
f"Дата проверки: {results['timestamp']}",
f"Хэш данных: {results['data_hash']}",
f"",
f"ОБЩИЙ БАЛЛ КАЧЕСТВА: {results['overall_score']:.1f}/100 ({results['quality_level'].upper()})",
f"",
f"БАЗОВАЯ СТАТИСТИКА:",
f" Размерность: {results['basic_statistics']['shape']}",
f" Использование памяти: {results['basic_statistics']['memory_usage_mb']:.2f} MB",
f" Числовые колонки: {results['basic_statistics']['numeric_columns']}",
f" Категориальные колонки: {results['basic_statistics']['categorical_columns']}",
f""
]

# Добавляем информацию о проблемах
issues_sections = [
("ПРОПУЩЕННЫЕ ЗНАЧЕНИЯ", results["missing_values"]),
("ДУБЛИКАТЫ", results["duplicates"]),
("ВЫБРОСЫ", results["outliers"]),
("ТИПЫ ДАННЫХ", results["data_types"]),
("ДИАПАЗОНЫ ЗНАЧЕНИЙ", results["value_ranges"]),
("СОГЛАСОВАННОСТЬ", results["consistency"]),
("ПОЛНОТА", results["completeness"]),
("ВАЛИДНОСТЬ", results["validity"])
]

for section_name, section_data in issues_sections:
if section_data.get("issues_found") or section_data.get("threshold_exceeded"):
report_lines.append(f"{section_name}: ПРОБЛЕМЫ НАЙДЕНЫ ({section_data['severity'].upper()})")
else:
report_lines.append(f"{section_name}: OK")

return "\\n".join(report_lines)

def save_quality_report(self, results: Dict[str, Any], file_path: str) -> bool:
"""
Сохраняет отчет о качестве в файл.

Args:
results: Результаты проверки качества
file_path: Путь к файлу

Returns:
True если успешно сохранено
"""
try:
# Создаем директорию если не существует
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Сохраняем JSON отчет
with open(file_path, 'w', encoding='utf-8') as f:
json.dump(results, f, indent=2, ensure_ascii=False, default=str)

# Сохраняем текстовый отчет
text_file_path = file_path.replace('.json', '_report.txt')
with open(text_file_path, 'w', encoding='utf-8') as f:
f.write(self.generate_quality_report(results))

logger.info(f"Отчет о качестве сохранен: {file_path}")
return True

except Exception as e:
logger.error(f"Ошибка сохранения отчета о качестве: {str(e)}")
return False
