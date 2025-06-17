#!/usr/bin/env python3
"""
Тестирование настройки SQLite для Airflow
"""

import os
import sqlite3
from pathlib import Path

def test_sqlite_setup():
"""Тестируем настройку SQLite"""

airflow_home = os.environ.get('AIRFLOW_HOME')
print(f"AIRFLOW_HOME: {airflow_home}")

if not airflow_home:
print(" AIRFLOW_HOME не установлен")
return False

# Проверяем директорию
airflow_path = Path(airflow_home)
if not airflow_path.exists():
print(f" Директория {airflow_home} не существует")
return False

print(f" Директория {airflow_home} существует")

# Проверяем конфигурационный файл
config_file = airflow_path / "airflow.cfg"
if not config_file.exists():
print(f" Конфигурационный файл {config_file} не найден")
return False

print(f" Конфигурационный файл найден: {config_file}")

# Читаем конфигурацию SQLite
with open(config_file, 'r') as f:
config_content = f.read()

if 'sql_alchemy_conn = sqlite://' in config_content:
print(" SQLite конфигурация найдена в airflow.cfg")

# Извлекаем путь к базе данных
lines = config_content.split('\n')
for line in lines:
if line.startswith('sql_alchemy_conn = sqlite://'):
db_path = line.replace('sql_alchemy_conn = sqlite://', '').strip()
print(f" Путь к базе данных: {db_path}")

# Создаем простую таблицу для теста
try:
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Создаем простую тестовую таблицу
cursor.execute('''
CREATE TABLE IF NOT EXISTS test_connection (
id INTEGER PRIMARY KEY,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('INSERT INTO test_connection (id) VALUES (1)')
conn.commit()

# Проверяем, что данные записались
cursor.execute('SELECT * FROM test_connection')
results = cursor.fetchall()

if results:
print(f" SQLite база работает! Записей: {len(results)}")
print(f" Данные: {results}")

conn.close()
return True

except Exception as e:
print(f" Ошибка работы с SQLite: {e}")
return False
else:
print(" SQLite конфигурация не найдена")
return False

if __name__ == "__main__":
print(" Тестирование настройки SQLite для Airflow")
print("=" * 50)

success = test_sqlite_setup()

if success:
print("\n Тест SQLite успешно пройден!")
else:
print("\n Тест SQLite не пройден!")
