#!/usr/bin/env python3
"""
Исправление базы данных Airflow для правильной папки (airflow, не airflow_home)
"""

import os
import sqlite3
import sys
from pathlib import Path

def fix_airflow_database():
"""Исправляем базу данных Airflow в правильной папке"""

# Получаем путь к проекту
project_root = Path(__file__).parent

# Правильная папка для Airflow
airflow_home = project_root / "airflow"
db_path = airflow_home / "airflow.db"

print(f" Исправление базы данных Airflow")
print(f" AIRFLOW_HOME: {airflow_home}")
print(f" База данных: {db_path}")

# Устанавливаем переменную окружения
os.environ['AIRFLOW_HOME'] = str(airflow_home)

# Создаем директорию если не существует
airflow_home.mkdir(exist_ok=True)

try:
# Подключаемся к базе данных
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Проверяем существующие таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
existing_tables = [row[0] for row in cursor.fetchall()]

print(f" Существующие таблицы: {len(existing_tables)}")

# Создаем таблицу variable если её нет
if 'variable' not in existing_tables:
print(" Создаем таблицу variable...")
cursor.execute('''
CREATE TABLE variable (
id INTEGER PRIMARY KEY AUTOINCREMENT,
key VARCHAR(250) NOT NULL UNIQUE,
val TEXT,
description TEXT,
is_encrypted BOOLEAN DEFAULT 0
)
''')
print(" Таблица variable создана")
else:
print(" Таблица variable уже существует")

# Создаем таблицу connection если её нет 
if 'connection' not in existing_tables:
print(" Создаем таблицу connection...")
cursor.execute('''
CREATE TABLE connection (
id INTEGER PRIMARY KEY AUTOINCREMENT,
conn_id VARCHAR(250) NOT NULL UNIQUE,
conn_type VARCHAR(500),
description TEXT,
host VARCHAR(500),
schema VARCHAR(500),
login VARCHAR(500),
password VARCHAR(5000),
port INTEGER,
extra TEXT,
is_encrypted BOOLEAN DEFAULT 0,
is_extra_encrypted BOOLEAN DEFAULT 0
)
''')
print(" Таблица connection создана")
else:
print(" Таблица connection уже существует")

# Создаем другие важные таблицы
tables_to_create = {
'dag': '''
CREATE TABLE dag (
dag_id VARCHAR(250) PRIMARY KEY,
root_dag_id VARCHAR(250),
is_paused BOOLEAN DEFAULT 1,
is_subdag BOOLEAN DEFAULT 0,
is_active BOOLEAN DEFAULT 0,
last_parsed_time TIMESTAMP,
last_pickled TIMESTAMP,
last_expired TIMESTAMP,
scheduler_lock BOOLEAN DEFAULT 0,
pickle_id INTEGER,
fileloc VARCHAR(2000),
owners VARCHAR(2000),
description TEXT,
default_view VARCHAR(25),
schedule_interval TEXT,
timetable_description TEXT,
max_active_tasks INTEGER DEFAULT 16,
max_active_runs INTEGER DEFAULT 16,
has_task_concurrency_limits BOOLEAN DEFAULT 0,
has_import_errors BOOLEAN DEFAULT 0,
next_dagrun TIMESTAMP,
next_dagrun_data_interval_start TIMESTAMP,
next_dagrun_data_interval_end TIMESTAMP,
next_dagrun_create_after TIMESTAMP
)
''',
'dag_run': '''
CREATE TABLE dag_run (
id INTEGER PRIMARY KEY AUTOINCREMENT,
dag_id VARCHAR(250) NOT NULL,
queued_at TIMESTAMP,
execution_date TIMESTAMP NOT NULL,
start_date TIMESTAMP,
end_date TIMESTAMP,
state VARCHAR(50),
run_id VARCHAR(250) NOT NULL,
creating_job_id INTEGER,
external_trigger BOOLEAN DEFAULT 1,
run_type VARCHAR(50) NOT NULL,
conf BLOB,
data_interval_start TIMESTAMP,
data_interval_end TIMESTAMP,
last_scheduling_decision TIMESTAMP,
log_template_id INTEGER,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
clear_number INTEGER DEFAULT 0,
UNIQUE (dag_id, execution_date),
UNIQUE (dag_id, run_id)
)
'''
}

for table_name, create_sql in tables_to_create.items():
if table_name not in existing_tables:
print(f" Создаем таблицу {table_name}...")
cursor.execute(create_sql)
print(f" Таблица {table_name} создана")
else:
print(f" Таблица {table_name} уже существует")

# Сохраняем изменения
conn.commit()

# Проверяем финальное состояние
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
final_tables = [row[0] for row in cursor.fetchall()]

print(f"\n Итоговое количество таблиц: {len(final_tables)}")
print(f" Таблицы: {', '.join(sorted(final_tables))}")

# Проверяем таблицу variable
cursor.execute("SELECT COUNT(*) FROM variable")
var_count = cursor.fetchone()[0]
print(f" Записей в таблице variable: {var_count}")

conn.close()

print(f"\n База данных успешно исправлена!")
print(f" Путь: {db_path}")
print(f" Размер файла: {db_path.stat().st_size} байт")

return True

except Exception as e:
print(f" Ошибка при работе с базой данных: {e}")
return False

if __name__ == "__main__":
print(" Исправление базы данных Airflow")
print("=" * 50)

success = fix_airflow_database()

if success:
print("\n Исправление завершено успешно!")
print(" Теперь можно запускать Airflow с правильной папкой")
else:
print("\n Исправление не удалось")
sys.exit(1)
