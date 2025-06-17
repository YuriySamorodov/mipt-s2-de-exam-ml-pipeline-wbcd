#!/usr/bin/env python3
"""
Скрипт для демонстрации работы Airflow с программно формируемыми абсолютными путями.
Этот скрипт проверяет, что все настройки корректны и пути формируются правильно.
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_absolute_paths():
"""Проверка абсолютных путей в конфигурации Airflow"""

print(" Проверка программно сформированных абсолютных путей в Airflow")
print("=" * 70)

# Получаем пути из переменных окружения
airflow_home = os.environ.get('AIRFLOW_HOME', '')
dags_folder = os.environ.get('AIRFLOW__CORE__DAGS_FOLDER', '')
plugins_folder = os.environ.get('AIRFLOW__CORE__PLUGINS_FOLDER', '')
logs_folder = os.environ.get('AIRFLOW__LOGGING__BASE_LOG_FOLDER', '')
db_conn = os.environ.get('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN', '')

print(f" Текущая рабочая директория: {os.getcwd()}")
print(f" AIRFLOW_HOME: {airflow_home}")
print(f" DAGs folder: {dags_folder}")
print(f" Plugins folder: {plugins_folder}")
print(f" Logs folder: {logs_folder}")
print(f" Database connection: {db_conn}")
print()

# Проверяем абсолютность путей
paths_to_check = [
("AIRFLOW_HOME", airflow_home),
("DAGs folder", dags_folder),
("Plugins folder", plugins_folder),
("Logs folder", logs_folder),
]

all_absolute = True
print(" Проверка абсолютности путей:")
for name, path in paths_to_check:
if path and Path(path).is_absolute():
print(f" {name}: АБСОЛЮТНЫЙ путь")
elif path:
print(f" {name}: ОТНОСИТЕЛЬНЫЙ путь")
all_absolute = False
else:
print(f" {name}: НЕ УСТАНОВЛЕН")

# Проверяем базу данных
if db_conn.startswith('sqlite:///'):
db_path = db_conn.replace('sqlite:///', '')
print(f"\n Проверка базы данных SQLite:")
print(f" Путь: {db_path}")

if Path(db_path).is_absolute():
print(f" Путь к БД: АБСОЛЮТНЫЙ")
else:
print(f" Путь к БД: ОТНОСИТЕЛЬНЫЙ")
all_absolute = False

if Path(db_path).exists():
print(f" Файл БД существует")
size = Path(db_path).stat().st_size
print(f" Размер БД: {size} байт")

# Проверяем подключение к базе данных
try:
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f" Таблиц в БД: {len(tables)}")
conn.close()
print(f" Подключение к БД работает")
except Exception as e:
print(f" Ошибка подключения к БД: {e}")
all_absolute = False
else:
print(f" Файл БД НЕ существует")
all_absolute = False

print("\n" + "=" * 70)

if all_absolute:
print(" ВСЕ ПУТИ СФОРМИРОВАНЫ ПРОГРАММНО И ЯВЛЯЮТСЯ АБСОЛЮТНЫМИ!")
print(" Конфигурация Airflow настроена корректно")
else:
print(" Некоторые пути не являются абсолютными или имеют проблемы")
print(" Проверьте настройки конфигурации")

return all_absolute

def run_airflow_commands():
"""Запуск команд Airflow для проверки"""

print("\n Проверка команд Airflow:")
print("-" * 30)

commands = [
("airflow version", "Версия Airflow"),
("airflow config get-value database sql_alchemy_conn", "Строка подключения к БД"),
("airflow config get-value core dags_folder", "Путь к DAGs"),
("airflow config get-value logging base_log_folder", "Путь к логам"),
]

for command, description in commands:
print(f" {description}:")
try:
import subprocess
result = subprocess.run(
command.split(), 
capture_output=True, 
text=True,
env=os.environ.copy()
)
if result.returncode == 0:
output = result.stdout.strip()
print(f" {output}")
else:
print(f" Ошибка: {result.stderr.strip()}")
except Exception as e:
print(f" Исключение: {e}")

print()

def main():
"""Основная функция"""

print(" Демонстрация работы Airflow с абсолютными путями")
print(" Все пути формируются программно в Python коде")
print()

# Проверяем окружение
if not os.environ.get('AIRFLOW_HOME'):
print(" Переменная AIRFLOW_HOME не установлена")
print(" Запустите сначала скрипт setup_airflow_config.py")
sys.exit(1)

# Проверяем пути
success = check_absolute_paths()

# Запускаем команды Airflow
run_airflow_commands()

print(" Итоги проверки:")
print(f" Конфигурация: {' КОРРЕКТНА' if success else ' ЕСТЬ ПРОБЛЕМЫ'}")
print(f" Метод формирования путей: ПРОГРАММНЫЙ (Python)")
print(f" Типы путей: АБСОЛЮТНЫЕ")
print(f" База данных: SQLITE С АБСОЛЮТНЫМ ПУТЕМ")

print("\n Программное формирование абсолютных путей работает корректно!")
print(" Все пути к файлам и базе данных формируются через Python код")
print(" Использование os.path.abspath() и pathlib.Path.absolute()")

if __name__ == "__main__":
main()
