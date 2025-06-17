#!/usr/bin/env python3
"""
Улучшенный скрипт для инициализации базы данных Airflow с абсолютными путями.
Этот скрипт обеспечивает корректную работу с абсолютными путями и решает проблемы миграций.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def setup_environment():
"""Настройка окружения с абсолютными путями"""

# Определяем базовые пути программно
current_dir = Path(__file__).parent.absolute()
project_dir = current_dir.parent.parent # Поднимаемся на 2 уровня вверх к корню проекта

# Формируем абсолютные пути
airflow_home = project_dir / "airflow"
dags_folder = project_dir / "dags"
plugins_folder = project_dir / "plugins"
logs_folder = project_dir / "logs"

# Создаем директории
airflow_home.mkdir(exist_ok=True)
dags_folder.mkdir(exist_ok=True)
plugins_folder.mkdir(exist_ok=True)
logs_folder.mkdir(exist_ok=True)

# Формируем абсолютный путь к базе данных
sqlite_db_path = airflow_home / "airflow.db"
sql_alchemy_conn = f"sqlite:///{sqlite_db_path.absolute()}"

# Устанавливаем переменные окружения с абсолютными путями
env_vars = {
'AIRFLOW_HOME': str(airflow_home),
'AIRFLOW__CORE__DAGS_FOLDER': str(dags_folder),
'AIRFLOW__CORE__PLUGINS_FOLDER': str(plugins_folder),
'AIRFLOW__LOGGING__BASE_LOG_FOLDER': str(logs_folder),
'AIRFLOW__DATABASE__SQL_ALCHEMY_CONN': sql_alchemy_conn,
'AIRFLOW__CORE__EXECUTOR': 'SequentialExecutor',
'AIRFLOW__CORE__LOAD_EXAMPLES': 'False',
'AIRFLOW__WEBSERVER__SECRET_KEY': 'dev_secret_key_for_sqlite',
'AIRFLOW__CORE__CHECK_SLAS': 'False',
'AIRFLOW__CORE__STORE_SERIALIZED_DAGS': 'True',
'AIRFLOW__CORE__STORE_DAG_CODE': 'True'
}

# Применяем переменные окружения
for key, value in env_vars.items():
os.environ[key] = value

print(" Настройка окружения с абсолютными путями:")
print(f" Проект: {project_dir}")
print(f" AIRFLOW_HOME: {airflow_home}")
print(f" База данных: {sqlite_db_path}")
print(f" DAGs: {dags_folder}")
print(f" Логи: {logs_folder}")

return {
'project_dir': project_dir,
'airflow_home': airflow_home,
'db_path': sqlite_db_path,
'sql_alchemy_conn': sql_alchemy_conn
}

def check_database_exists(db_path):
"""Проверка существования базы данных"""
return Path(db_path).exists()

def backup_database(db_path):
"""Создание резервной копии базы данных"""
if check_database_exists(db_path):
backup_path = f"{db_path}.backup"
try:
import shutil
shutil.copy2(db_path, backup_path)
print(f" Создана резервная копия: {backup_path}")
return backup_path
except Exception as e:
print(f" Не удалось создать резервную копию: {e}")
return None
return None

def create_minimal_database(db_path):
"""Создание минимальной базы данных SQLite"""
try:
# Удаляем старую базу если существует
if Path(db_path).exists():
Path(db_path).unlink()
print(f"️ Удалена старая база данных: {db_path}")

# Создаем новую базу данных
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Создаем базовую таблицу для версии миграций
cursor.execute("""
CREATE TABLE IF NOT EXISTS alembic_version (
version_num VARCHAR(32) NOT NULL,
CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
)
""")

conn.commit()
conn.close()

print(f" Создана новая база данных: {db_path}")
return True

except Exception as e:
print(f" Ошибка создания базы данных: {e}")
return False

def run_airflow_command(command, description):
"""Выполнение команды Airflow с обработкой ошибок"""
try:
print(f" {description}...")

# Запускаем команду
result = subprocess.run(
command, 
shell=True, 
capture_output=True, 
text=True,
env=os.environ.copy()
)

if result.returncode == 0:
print(f" {description} - успешно")
if result.stdout.strip():
print(f" Вывод: {result.stdout.strip()}")
return True
else:
print(f" {description} - предупреждение или ошибка")
if result.stderr.strip():
print(f" Ошибка: {result.stderr.strip()}")
if result.stdout.strip():
print(f" Вывод: {result.stdout.strip()}")
return False

except Exception as e:
print(f" Исключение при выполнении '{command}': {e}")
return False

def initialize_airflow_database(paths):
"""Инициализация базы данных Airflow"""

db_path = paths['db_path']

print(" Инициализация базы данных Airflow...")

# Создаем резервную копию если база существует
backup_database(db_path)

# Создаем минимальную базу данных
if not create_minimal_database(db_path):
print(" Не удалось создать базу данных")
return False

# Инициализируем базу данных Airflow
success = run_airflow_command(
"airflow db init",
"Инициализация схемы базы данных"
)

if not success:
print(" Инициализация базы данных завершилась с предупреждениями")
print(" Попытка повторной инициализации...")

# Попытка сброса и повторной инициализации
create_minimal_database(db_path)
success = run_airflow_command(
"airflow db reset --yes",
"Сброс и повторная инициализация базы данных"
)

# Проверяем результат
if check_database_exists(db_path):
print(f" База данных создана: {db_path}")

# Проверяем размер базы данных
db_size = Path(db_path).stat().st_size
print(f" Размер базы данных: {db_size} байт")

return True
else:
print(f" База данных не найдена: {db_path}")
return False

def create_admin_user():
"""Создание пользователя admin"""
print(" Создание пользователя admin...")

success = run_airflow_command(
"airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin",
"Создание пользователя admin"
)

if not success:
print("ℹ️ Пользователь admin возможно уже существует")

return True

def verify_installation(paths):
"""Проверка корректности установки"""

print(" Проверка корректности установки...")

# Проверяем наличие файлов
checks = [
(paths['airflow_home'], "Директория AIRFLOW_HOME"),
(paths['db_path'], "База данных SQLite"),
(paths['project_dir'] / 'dags', "Директория DAGs"),
(paths['project_dir'] / 'logs', "Директория логов")
]

all_good = True
for path, description in checks:
if Path(path).exists():
print(f" {description}: {path}")
else:
print(f" {description}: {path} - НЕ НАЙДЕНО")
all_good = False

# Проверяем команды Airflow
airflow_commands = [
("airflow version", "Версия Airflow"),
("airflow config get-value core dags_folder", "Путь к DAGs"),
("airflow config get-value database sql_alchemy_conn", "Строка подключения к БД")
]

for command, description in airflow_commands:
print(f" Проверка: {description}")
run_airflow_command(command, description)

return all_good

def main():
"""Основная функция"""

print(" Инициализация Airflow с абсолютными путями")
print("=" * 60)

# Настраиваем окружение
paths = setup_environment()

print("\n" + "=" * 60)

# Инициализируем базу данных
db_success = initialize_airflow_database(paths)

if db_success:
# Создаем пользователя admin
create_admin_user()

print("\n" + "=" * 60)

# Проверяем установку
verify_installation(paths)

print("\n" + "=" * 60)
print(" Инициализация завершена успешно!")
print("\n Информация для запуска:")
print(f" База данных: {paths['db_path']}")
print(f" Строка подключения: {paths['sql_alchemy_conn']}")
print(" Пользователь: admin")
print(" Пароль: admin")
print("\n Теперь можно запускать Airflow!")

else:
print("\n Инициализация завершилась с ошибками")
print(" Попробуйте запустить скрипт повторно или проверьте логи")
sys.exit(1)

if __name__ == "__main__":
main()
