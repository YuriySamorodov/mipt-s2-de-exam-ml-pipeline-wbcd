#!/usr/bin/env python3
"""
Тестовый скрипт для проверки всех конфигураций Airflow.
Этот скрипт проверяет корректность генерации конфигураций для всех режимов развертывания.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
"""Выполнение команды с выводом результата"""
print(f"\n {description}")
print("=" * 60)

try:
result = subprocess.run(command, shell=True, capture_output=True, text=True)
if result.returncode == 0:
print(" Команда выполнена успешно")
print(result.stdout)
else:
print(" Ошибка выполнения команды")
print(result.stderr)
return result.returncode == 0
except Exception as e:
print(f" Исключение при выполнении команды: {e}")
return False

def test_configuration_scripts():
"""Тестирование всех скриптов конфигурации"""

print(" ТЕСТИРОВАНИЕ ВСЕХ КОНФИГУРАЦИЙ AIRFLOW")
print(" Программное формирование абсолютных путей для разных режимов развертывания")
print("=" * 80)

# Определяем директорию проекта
project_dir = Path(__file__).parent.absolute()
os.chdir(project_dir)

print(f" Директория проекта: {project_dir}")

# Тесты для всех режимов
tests = [
{
'mode': 'SQLite (порт 8081)',
'command': 'python setup_airflow_config.py',
'env_command': 'python set_absolute_paths_env.py',
'port': '8081',
'executor': 'SequentialExecutor',
'database': 'SQLite'
},
{
'mode': 'PostgreSQL (порт 8082)',
'command': 'python setup_airflow_config.py --postgres',
'env_command': 'python set_absolute_paths_env.py --postgres',
'port': '8082',
'executor': 'LocalExecutor',
'database': 'PostgreSQL'
},
{
'mode': 'Docker (порт 8083)',
'command': 'python setup_airflow_config.py --docker',
'env_command': 'python set_absolute_paths_env.py --docker',
'port': '8083',
'executor': 'LocalExecutor',
'database': 'PostgreSQL'
}
]

results = []

for test in tests:
print(f"\n ТЕСТИРОВАНИЕ РЕЖИМА: {test['mode']}")
print("─" * 50)

# Тест генерации конфигурации
config_success = run_command(
test['command'],
f"Генерация конфигурации для {test['mode']}"
)

# Тест генерации переменных окружения
env_success = run_command(
test['env_command'],
f"Генерация переменных окружения для {test['mode']}"
)

# Проверка содержимого airflow.cfg
cfg_success = check_airflow_config(test)

success = config_success and env_success and cfg_success
results.append({
'mode': test['mode'],
'success': success,
'config': config_success,
'env': env_success,
'cfg_check': cfg_success
})

status = " УСПЕШНО" if success else " ОШИБКА"
print(f"\n{status} - {test['mode']}")

# Итоговый отчет
print_final_report(results)

return all(result['success'] for result in results)

def check_airflow_config(test_config):
"""Проверка содержимого файла airflow.cfg"""

try:
config_path = Path("airflow/airflow.cfg")
if not config_path.exists():
print(" Файл airflow.cfg не найден")
return False

with open(config_path, 'r', encoding='utf-8') as f:
content = f.read()

print(f" Проверка airflow.cfg для {test_config['mode']}:")

# Проверяем порт
if f"web_server_port = {test_config['port']}" in content:
print(f" Порт: {test_config['port']}")
else:
print(f" Порт не соответствует ожидаемому: {test_config['port']}")
return False

# Проверяем исполнитель
if f"executor = {test_config['executor']}" in content:
print(f" Исполнитель: {test_config['executor']}")
else:
print(f" Исполнитель не соответствует ожидаемому: {test_config['executor']}")
return False

# Проверяем базу данных
if test_config['database'] == 'SQLite':
if "sqlite:////" in content:
print(f" База данных: SQLite (абсолютный путь)")
else:
print(f" База данных SQLite не настроена корректно")
return False
else: # PostgreSQL
if "postgresql+psycopg2://" in content:
print(f" База данных: PostgreSQL")
else:
print(f" База данных PostgreSQL не настроена корректно")
return False

# Проверяем абсолютные пути
project_path = str(Path(__file__).parent.absolute())
if project_path in content:
print(f" Абсолютные пути: корректно сформированы")
else:
print(f" Абсолютные пути не найдены")
return False

return True

except Exception as e:
print(f" Ошибка при проверке конфигурации: {e}")
return False

def print_final_report(results):
"""Вывод итогового отчета"""

print("\n" + "=" * 80)
print(" ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
print("=" * 80)

total_tests = len(results)
successful_tests = sum(1 for r in results if r['success'])

print(f" Всего тестов: {total_tests}")
print(f" Успешных: {successful_tests}")
print(f" Неудачных: {total_tests - successful_tests}")
print(f" Процент успеха: {(successful_tests/total_tests)*100:.1f}%")

print("\n Детальные результаты:")
for result in results:
status = "" if result['success'] else ""
print(f" {status} {result['mode']}")
print(f" - Конфигурация: {'' if result['config'] else ''}")
print(f" - Переменные окружения: {'' if result['env'] else ''}")
print(f" - Проверка airflow.cfg: {'' if result['cfg_check'] else ''}")

print("\n ЗАКЛЮЧЕНИЕ:")
if successful_tests == total_tests:
print(" ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
print(" Система готова к работе во всех режимах развертывания")
print(" Все пути формируются программно и являются абсолютными")
print(" Конфигурации корректно создаются для всех портов:")
print(" - SQLite: порт 8081")
print(" - PostgreSQL: порт 8082") 
print(" - Docker: порт 8083")
else:
print(" НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
print(" Требуется исправление ошибок перед развертыванием")

print("=" * 80)

def main():
"""Основная функция"""

print(" АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ КОНФИГУРАЦИЙ AIRFLOW")
print(" Цель: Проверить корректность программного формирования абсолютных путей")
print("")

try:
success = test_configuration_scripts()

if success:
print("\n ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
sys.exit(0)
else:
print("\n ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
sys.exit(1)

except KeyboardInterrupt:
print("\n⏹️ Тестирование прервано пользователем")
sys.exit(1)
except Exception as e:
print(f"\n Критическая ошибка тестирования: {e}")
sys.exit(1)

if __name__ == "__main__":
main()
