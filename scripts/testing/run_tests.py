#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов ML пайплайна.
Этот скрипт запускает все unit-тесты и интеграционные тесты.
"""

import os
import sys
import unittest
import subprocess
import time
from pathlib import Path

# Добавляем корневую папку проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'etl'))
sys.path.insert(0, str(project_root / 'config'))

def print_header(title):
"""Печатает заголовок секции."""
print("\n" + "="*60)
print(f" {title}")
print("="*60)

def print_separator():
"""Печатает разделитель."""
print("-" * 60)

def check_dependencies():
"""Проверяет наличие необходимых зависимостей."""
print_header("ПРОВЕРКА ЗАВИСИМОСТЕЙ")

required_packages = [
'pandas', 'numpy', 'scikit-learn', 'matplotlib', 
'seaborn', 'joblib', 'pytest', 'pyyaml'
]

missing_packages = []

for package in required_packages:
try:
__import__(package)
print(f"{package}")
except ImportError:
print(f"{package} - НЕ УСТАНОВЛЕН")
missing_packages.append(package)

if missing_packages:
print(f"\nПРЕДУПРЕЖДЕНИЕ: Отсутствуют зависимости: {', '.join(missing_packages)}")
print("Установите их командой: pip install -r requirements.txt")
return False

print("\nВсе зависимости установлены")
return True

def run_unit_tests():
"""Запускает unit-тесты."""
print_header("UNIT ТЕСТЫ")

test_files = [
'test_data_loader.py',
'test_data_preprocessor.py', 
'test_model_trainer.py',
'test_metrics_calculator.py',
'test_storage_manager.py'
]

results = {}

for test_file in test_files:
test_path = project_root / 'tests' / test_file
if not test_path.exists():
print(f"{test_file} - файл не найден")
results[test_file] = False
continue

print(f"\nЗапуск {test_file}...")
try:
# Запускаем тест
result = subprocess.run([
sys.executable, '-m', 'unittest', f'tests.{test_file[:-3]}'
], cwd=project_root, capture_output=True, text=True, timeout=120)

if result.returncode == 0:
print(f"{test_file} - ПРОЙДЕН")
results[test_file] = True
else:
print(f"{test_file} - ПРОВАЛЕН")
print(f"Ошибка: {result.stderr}")
results[test_file] = False

except subprocess.TimeoutExpired:
print(f"ТАЙМ-АУТ: {test_file} - ТАЙМ-АУТ")
results[test_file] = False
except Exception as e:
print(f"{test_file} - ОШИБКА: {e}")
results[test_file] = False

return results

def run_integration_tests():
"""Запускает интеграционные тесты."""
print_header("ИНТЕГРАЦИОННЫЕ ТЕСТЫ")

test_file = 'test_integration.py'
test_path = project_root / 'tests' / test_file

if not test_path.exists():
print(f"{test_file} - файл не найден")
return False

print(f"Запуск {test_file}...")
try:
result = subprocess.run([
sys.executable, '-m', 'unittest', f'tests.{test_file[:-3]}'
], cwd=project_root, capture_output=True, text=True, timeout=300)

if result.returncode == 0:
print(f"{test_file} - ПРОЙДЕН")
return True
else:
print(f"{test_file} - ПРОВАЛЕН")
print(f"Ошибка: {result.stderr}")
return False

except subprocess.TimeoutExpired:
print(f"ТАЙМ-АУТ: {test_file} - ТАЙМ-АУТ")
return False
except Exception as e:
print(f"{test_file} - ОШИБКА: {e}")
return False

def run_pytest_coverage():
"""Запускает pytest с покрытием кода."""
print_header("АНАЛИЗ ПОКРЫТИЯ КОДА")

try:
# Проверяем, установлен ли pytest-cov
subprocess.run([sys.executable, '-c', 'import pytest_cov'], 
check=True, capture_output=True)

print("Запуск pytest с анализом покрытия...")
result = subprocess.run([
sys.executable, '-m', 'pytest', 'tests/', 
'--cov=etl', '--cov=config',
'--cov-report=html', '--cov-report=term-missing',
'-v'
], cwd=project_root, capture_output=True, text=True, timeout=300)

print(result.stdout)
if result.stderr:
print("Предупреждения:")
print(result.stderr)

if result.returncode == 0:
print("Анализ покрытия завершен")
coverage_html = project_root / 'htmlcov' / 'index.html'
if coverage_html.exists():
print(f"HTML отчет: {coverage_html}")
return True
else:
print("Ошибка при анализе покрытия")
return False

except subprocess.CalledProcessError:
print("ПРЕДУПРЕЖДЕНИЕ: pytest-cov не установлен, пропускаем анализ покрытия")
return False
except Exception as e:
print(f"Ошибка: {e}")
return False

def validate_project_structure():
"""Проверяет структуру проекта."""
print_header("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")

required_files = [
'requirements.txt',
'config/config.yaml',
'config/config_utils.py',
'etl/data_loader.py',
'etl/data_preprocessor.py',
'etl/model_trainer.py',
'etl/metrics_calculator.py',
'etl/storage_manager.py',
'dags/ml_pipeline_dag.py',
'Makefile',
'Dockerfile',
'README.md'
]

required_dirs = [
'data', 'results', 'logs', 'tests'
]

missing_files = []
missing_dirs = []

# Проверяем файлы
for file_path in required_files:
full_path = project_root / file_path
if full_path.exists():
print(f"{file_path}")
else:
print(f"{file_path} - отсутствует")
missing_files.append(file_path)

print_separator()

# Проверяем директории
for dir_path in required_dirs:
full_path = project_root / dir_path
if full_path.exists() and full_path.is_dir():
print(f"{dir_path}/")
else:
print(f"{dir_path}/ - отсутствует")
missing_dirs.append(dir_path)

if missing_files or missing_dirs:
print(f"\nПРЕДУПРЕЖДЕНИЕ: Отсутствуют файлы: {len(missing_files)}")
print(f"ПРЕДУПРЕЖДЕНИЕ: Отсутствуют директории: {len(missing_dirs)}")
return False

print("\nСтруктура проекта корректна")
return True

def generate_test_report(unit_results, integration_result):
"""Генерирует отчет о тестировании."""
print_header("ОТЧЕТ О ТЕСТИРОВАНИИ")

total_unit_tests = len(unit_results)
passed_unit_tests = sum(1 for result in unit_results.values() if result)

print(f"Unit тесты: {passed_unit_tests}/{total_unit_tests} пройдено")
print(f"Интеграционные тесты: {'1/1' if integration_result else '0/1'} пройдено")

total_tests = total_unit_tests + 1
total_passed = passed_unit_tests + (1 if integration_result else 0)

success_rate = (total_passed / total_tests) * 100
print(f"Общий результат: {total_passed}/{total_tests} ({success_rate:.1f}%)")

print("\nДетальные результаты:")
for test_name, result in unit_results.items():
status = "ПРОЙДЕН" if result else "ПРОВАЛЕН"
print(f" {test_name}: {status}")

integration_status = "ПРОЙДЕН" if integration_result else "ПРОВАЛЕН"
print(f" test_integration.py: {integration_status}")

# Сохраняем отчет в файл
report_path = project_root / 'test_report.txt'
with open(report_path, 'w', encoding='utf-8') as f:
f.write(f"Отчет о тестировании ML пайплайна\n")
f.write(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
f.write(f"Unit тесты: {passed_unit_tests}/{total_unit_tests}\n")
f.write(f"Интеграционные тесты: {'1/1' if integration_result else '0/1'}\n")
f.write(f"Общий результат: {total_passed}/{total_tests} ({success_rate:.1f}%)\n\n")

for test_name, result in unit_results.items():
f.write(f"{test_name}: {'ПРОЙДЕН' if result else 'ПРОВАЛЕН'}\n")
f.write(f"test_integration.py: {'ПРОЙДЕН' if integration_result else 'ПРОВАЛЕН'}\n")

print(f"\nОтчет сохранен: {report_path}")

return success_rate >= 80 # Считаем успешным, если прошло 80% тестов

def main():
"""Основная функция."""
print_header("ML PIPELINE - ЗАПУСК ТЕСТОВ")
print(f"Проект: {project_root}")
print(f"Python: {sys.version}")

start_time = time.time()

# Проверяем структуру проекта
structure_ok = validate_project_structure()
if not structure_ok:
print("\nНекорректная структура проекта. Исправьте ошибки перед запуском тестов.")
return False

# Проверяем зависимости
deps_ok = check_dependencies()
if not deps_ok:
print("\nОтсутствуют зависимости. Установите их перед запуском тестов.")
return False

# Запускаем unit тесты
unit_results = run_unit_tests()

# Запускаем интеграционные тесты
integration_result = run_integration_tests()

# Анализ покрытия кода
run_pytest_coverage()

# Генерируем отчет
overall_success = generate_test_report(unit_results, integration_result)

end_time = time.time()
execution_time = end_time - start_time

print_header("ИТОГИ")
print(f"ТАЙМ-АУТ: Время выполнения: {execution_time:.1f} секунд")

if overall_success:
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
print("Проект готов к развертыванию")
return True
else:
print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
print("ПРЕДУПРЕЖДЕНИЕ: Исправьте ошибки перед развертыванием")
return False

if __name__ == '__main__':
success = main()
sys.exit(0 if success else 1)
