#!/usr/bin/env python3
"""
Скрипт для инициализации SQLite базы данных Airflow без миграций
"""

import sqlite3
import os
from pathlib import Path

def create_airflow_tables():
"""Создает основные таблицы Airflow в SQLite базе данных"""

airflow_home = os.environ.get('AIRFLOW_HOME')
if not airflow_home:
airflow_home = './airflow'

db_path = Path(airflow_home) / 'airflow.db'
print(f"Инициализация базы данных: {db_path}")

# Создаем подключение к базе данных
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
# Создаем таблицу variable
cursor.execute('''
CREATE TABLE IF NOT EXISTS variable (
id INTEGER PRIMARY KEY AUTOINCREMENT,
key VARCHAR(250) NOT NULL UNIQUE,
val TEXT NULL,
description TEXT NULL,
is_encrypted BOOLEAN NOT NULL DEFAULT 0
)
''')

# Создаем таблицу connection
cursor.execute('''
CREATE TABLE IF NOT EXISTS connection (
id INTEGER PRIMARY KEY AUTOINCREMENT,
conn_id VARCHAR(250) NOT NULL UNIQUE,
conn_type VARCHAR(500) NOT NULL,
description TEXT NULL,
host VARCHAR(500) NULL,
schema VARCHAR(500) NULL,
login VARCHAR(500) NULL,
password VARCHAR(500) NULL,
port INTEGER NULL,
extra TEXT NULL,
is_encrypted BOOLEAN NOT NULL DEFAULT 0,
is_extra_encrypted BOOLEAN NOT NULL DEFAULT 0
)
''')

# Создаем таблицу ab_user (пользователи)
cursor.execute('''
CREATE TABLE IF NOT EXISTS ab_user (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username VARCHAR(64) NOT NULL UNIQUE,
email VARCHAR(320) NOT NULL UNIQUE,
first_name VARCHAR(64) NOT NULL,
last_name VARCHAR(64) NOT NULL,
password VARCHAR(256) NULL,
active BOOLEAN NOT NULL DEFAULT 1,
created_on DATETIME NULL,
changed_on DATETIME NULL
)
''')

# Создаем таблицу dag
cursor.execute('''
CREATE TABLE IF NOT EXISTS dag (
dag_id VARCHAR(250) NOT NULL PRIMARY KEY,
root_dag_id VARCHAR(250) NULL,
is_paused BOOLEAN NOT NULL DEFAULT 1,
is_subdag BOOLEAN NOT NULL DEFAULT 0,
is_active BOOLEAN NOT NULL DEFAULT 0,
last_parsed_time DATETIME NULL,
last_pickled DATETIME NULL,
last_expired DATETIME NULL,
scheduler_lock DATETIME NULL,
pickle_id INTEGER NULL,
fileloc VARCHAR(2000) NOT NULL,
owners VARCHAR(2000) NULL,
description TEXT NULL,
default_view VARCHAR(25) NULL,
schedule_interval TEXT NULL,
max_active_tasks INTEGER NOT NULL DEFAULT 16,
max_active_runs INTEGER NULL,
has_task_concurrency_limits BOOLEAN NOT NULL DEFAULT 0,
has_import_errors BOOLEAN NOT NULL DEFAULT 0,
next_dagrun DATETIME NULL,
next_dagrun_data_interval_start DATETIME NULL,
next_dagrun_data_interval_end DATETIME NULL,
next_dagrun_create_after DATETIME NULL
)
''')

# Создаем таблицу task_instance
cursor.execute('''
CREATE TABLE IF NOT EXISTS task_instance (
task_id VARCHAR(250) NOT NULL,
dag_id VARCHAR(250) NOT NULL,
run_id VARCHAR(250) NOT NULL,
map_index INTEGER NOT NULL DEFAULT -1,
start_date DATETIME NULL,
end_date DATETIME NULL,
duration FLOAT NULL,
state VARCHAR(20) NULL,
try_number INTEGER NOT NULL DEFAULT 0,
max_tries INTEGER NOT NULL DEFAULT 0,
hostname VARCHAR(1000) NULL,
unixname VARCHAR(1000) NULL,
job_id INTEGER NULL,
pool VARCHAR(256) NOT NULL DEFAULT 'default_pool',
pool_slots INTEGER NOT NULL DEFAULT 1,
queue VARCHAR(256) NULL DEFAULT 'default',
priority_weight INTEGER NULL DEFAULT 1,
operator VARCHAR(1000) NULL,
queued_dttm DATETIME NULL,
queued_by_job_id INTEGER NULL,
pid INTEGER NULL,
executor_config BLOB NULL,
updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
rendered_map_index VARCHAR(250) NULL,
external_executor_id VARCHAR(250) NULL,
trigger_id INTEGER NULL,
trigger_timeout DATETIME NULL,
next_method VARCHAR(1000) NULL,
next_kwargs JSON NULL,
PRIMARY KEY (dag_id, task_id, run_id, map_index)
)
''')

# Создаем таблицу dag_run
cursor.execute('''
CREATE TABLE IF NOT EXISTS dag_run (
id INTEGER PRIMARY KEY AUTOINCREMENT,
dag_id VARCHAR(250) NOT NULL,
queued_at DATETIME NULL,
execution_date DATETIME NOT NULL,
start_date DATETIME NULL,
end_date DATETIME NULL,
state VARCHAR(50) NULL,
run_id VARCHAR(250) NOT NULL,
creating_job_id INTEGER NULL,
external_trigger BOOLEAN NULL DEFAULT 1,
run_type VARCHAR(50) NOT NULL,
conf BLOB NULL,
data_interval_start DATETIME NULL,
data_interval_end DATETIME NULL,
last_scheduling_decision DATETIME NULL,
dag_hash VARCHAR(32) NULL,
log_template_id INTEGER NULL,
updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
clear_number INTEGER NOT NULL DEFAULT 0,
UNIQUE (dag_id, execution_date),
UNIQUE (dag_id, run_id)
)
''')

# Создаем таблицу xcom
cursor.execute('''
CREATE TABLE IF NOT EXISTS xcom (
dag_run_id INTEGER NOT NULL,
task_id VARCHAR(250) NOT NULL,
map_index INTEGER NOT NULL DEFAULT -1,
key VARCHAR(512) NOT NULL,
value BLOB NULL,
timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
dag_id VARCHAR(250) NOT NULL,
run_id VARCHAR(250) NOT NULL,
PRIMARY KEY (dag_run_id, task_id, map_index, key)
)
''')

# Создаем таблицу log
cursor.execute('''
CREATE TABLE IF NOT EXISTS log (
id INTEGER PRIMARY KEY AUTOINCREMENT,
dttm DATETIME NULL,
dag_id VARCHAR(250) NULL,
task_id VARCHAR(250) NULL,
map_index INTEGER NOT NULL DEFAULT -1,
event VARCHAR(30) NULL,
execution_date DATETIME NULL,
owner VARCHAR(500) NULL,
extra TEXT NULL
)
''')

# Создаем таблицу job
cursor.execute('''
CREATE TABLE IF NOT EXISTS job (
id INTEGER PRIMARY KEY AUTOINCREMENT,
dag_id VARCHAR(250) NULL,
state VARCHAR(20) NULL,
job_type VARCHAR(30) NULL,
start_date DATETIME NULL,
end_date DATETIME NULL,
latest_heartbeat DATETIME NULL,
executor_class VARCHAR(500) NULL,
hostname VARCHAR(500) NULL,
unixname VARCHAR(1000) NULL
)
''')

# Вставляем админа по умолчанию, если его нет
cursor.execute('''
INSERT OR IGNORE INTO ab_user 
(username, email, first_name, last_name, password, active, created_on, changed_on)
VALUES 
('admin', 'admin@example.com', 'Admin', 'User', 'pbkdf2:sha256:260000$hash', 1, datetime('now'), datetime('now'))
''')

# Добавляем стандартные переменные
cursor.execute('''
INSERT OR IGNORE INTO variable (key, val, description)
VALUES ('AIRFLOW__CORE__LOAD_EXAMPLES', 'False', 'Disable example DAGs')
''')

conn.commit()
print(" Основные таблицы Airflow созданы успешно!")

# Проверяем созданные таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f" Созданные таблицы: {[table[0] for table in tables]}")

# Проверяем таблицу variable
cursor.execute("SELECT COUNT(*) FROM variable")
var_count = cursor.fetchone()[0]
print(f" Переменных в базе: {var_count}")

return True

except Exception as e:
print(f" Ошибка при создании таблиц: {e}")
return False

finally:
conn.close()

if __name__ == "__main__":
print(" Инициализация базы данных Airflow SQLite")
print("=" * 50)

success = create_airflow_tables()

if success:
print("\n База данных успешно инициализирована!")
print("Теперь можно запускать Airflow.")
else:
print("\n Не удалось инициализировать базу данных.")
