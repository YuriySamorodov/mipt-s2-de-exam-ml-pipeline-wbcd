#!/usr/bin/env python3
"""
Скрипт для установки переменных окружения Airflow с абсолютными путями.
Этот скрипт генерирует команды export для bash, которые устанавливают
все переменные окружения с программно сформированными абсолютными путями.
"""

import os
import sys
from pathlib import Path

def generate_environment_exports(use_postgres=False, use_docker=False):
"""Генерация команд export с абсолютными путями"""

# Определяем базовые пути программно
current_dir = Path(__file__).parent.absolute()
project_dir = current_dir

# Формируем абсолютные пути
airflow_home = project_dir / "airflow"
dags_folder = project_dir / "dags"
plugins_folder = project_dir / "plugins"
logs_folder = project_dir / "logs"

# Создаем директории если они не существуют
airflow_home.mkdir(exist_ok=True)
dags_folder.mkdir(exist_ok=True)
plugins_folder.mkdir(exist_ok=True)
logs_folder.mkdir(exist_ok=True)

# Определяем порт и настройки в зависимости от режима
if use_docker:
port = '8083'
executor = 'LocalExecutor'
workers = '4'
secret_key = 'dev_secret_key_for_docker'
elif use_postgres:
port = '8082'
executor = 'LocalExecutor'
workers = '4'
secret_key = 'dev_secret_key_for_postgres'
else:
port = '8081'
executor = 'SequentialExecutor'
workers = '1'
secret_key = 'dev_secret_key_for_sqlite'

# Формируем строку подключения к базе данных
if use_postgres or use_docker:
sql_alchemy_conn = "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
sqlite_db_path = 'N/A (PostgreSQL)'
else:
sqlite_db_path = airflow_home / "airflow.db"
sql_alchemy_conn = f"sqlite:///{sqlite_db_path.absolute()}"

# Словарь переменных окружения с абсолютными путями
env_vars = {
'AIRFLOW_HOME': str(airflow_home),
'AIRFLOW__CORE__DAGS_FOLDER': str(dags_folder),
'AIRFLOW__CORE__PLUGINS_FOLDER': str(plugins_folder),
'AIRFLOW__LOGGING__BASE_LOG_FOLDER': str(logs_folder),
'AIRFLOW__DATABASE__SQL_ALCHEMY_CONN': sql_alchemy_conn,
'AIRFLOW__CORE__EXECUTOR': executor,
'AIRFLOW__CORE__LOAD_EXAMPLES': 'False',
'AIRFLOW__WEBSERVER__SECRET_KEY': secret_key,
'AIRFLOW__WEBSERVER__WEB_SERVER_PORT': port,
'AIRFLOW__CORE__CHECK_SLAS': 'False',
'AIRFLOW__CORE__STORE_SERIALIZED_DAGS': 'True',
'AIRFLOW__CORE__STORE_DAG_CODE': 'True',
'AIRFLOW__WEBSERVER__EXPOSE_CONFIG': 'True',
'AIRFLOW__WEBSERVER__WORKERS': workers,
'AIRFLOW__WEBSERVER__WORKER_TIMEOUT': '300'
}

return env_vars, {
'project_dir': project_dir,
'airflow_home': airflow_home,
'dags_folder': dags_folder,
'plugins_folder': plugins_folder,
'logs_folder': logs_folder,
'sqlite_db_path': sqlite_db_path,
'sql_alchemy_conn': sql_alchemy_conn,
'port': port,
'executor': executor,
'deployment_mode': 'Docker' if use_docker else 'PostgreSQL' if use_postgres else 'SQLite'
}

def set_environment_variables(use_postgres=False, use_docker=False):
"""Установка переменных окружения в текущем процессе"""

env_vars, paths = generate_environment_exports(use_postgres, use_docker)

deployment_name = f"{paths['deployment_mode']} (порт {paths['port']})"

print(f" Установка переменных окружения с абсолютными путями - {deployment_name}:")
print(f" Проект: {paths['project_dir']}")
print(f" AIRFLOW_HOME: {paths['airflow_home']}")
print(f" DAGs: {paths['dags_folder']}")
print(f" Plugins: {paths['plugins_folder']}")
print(f" Логи: {paths['logs_folder']}")
print(f" БД: {paths['sqlite_db_path']}")
print(f" Порт: {paths['port']}")
print(f" Исполнитель: {paths['executor']}")
print()

# Устанавливаем переменные в текущем окружении
for key, value in env_vars.items():
os.environ[key] = value
print(f"export {key}='{value}'")

print()
print(f" Все переменные окружения установлены с абсолютными путями для {deployment_name}!")

return env_vars, paths

def generate_export_script(use_postgres=False, use_docker=False):
"""Генерация скрипта с командами export"""

env_vars, paths = generate_environment_exports(use_postgres, use_docker)

deployment_name = f"{paths['deployment_mode']} (порт {paths['port']})"

script_content = f"""#!/bin/bash
# Автоматически сгенерированный скрипт с переменными окружения Airflow
# Все пути программно сформированы как абсолютные
# Режим развертывания: {deployment_name}

echo " Установка переменных окружения Airflow с абсолютными путями..."
echo " Режим: {deployment_name}"

# Экспорт переменных окружения
"""

for key, value in env_vars.items():
script_content += f'export {key}="{value}"\n'

script_content += f"""
echo " Переменные окружения установлены:"
echo " Проект: {paths['project_dir']}"
echo " AIRFLOW_HOME: {paths['airflow_home']}"
echo " DAGs: {paths['dags_folder']}" 
echo " Plugins: {paths['plugins_folder']}"
echo " Логи: {paths['logs_folder']}"
echo " БД: {paths['sqlite_db_path']}"
echo " Порт: {paths['port']}"
echo " Исполнитель: {paths['executor']}"
echo ""
echo " Все пути сформированы программно и являются абсолютными!"
echo " Режим развертывания: {deployment_name}"
"""

# Определяем имя файла в зависимости от режима
if use_docker:
script_name = "set_airflow_env_docker.sh"
elif use_postgres:
script_name = "set_airflow_env_postgres.sh"
else:
script_name = "set_airflow_env_sqlite.sh"

# Записываем скрипт в файл
script_path = paths['project_dir'] / script_name
with open(script_path, 'w', encoding='utf-8') as f:
f.write(script_content)

# Делаем скрипт исполняемым
os.chmod(script_path, 0o755)

print(f" Создан скрипт: {script_path}")
return str(script_path)

def main():
"""Основная функция"""

# Проверяем аргументы командной строки
use_postgres = '--postgres' in sys.argv
use_docker = '--docker' in sys.argv

# Определяем режим развертывания
if use_docker:
deployment_mode = 'Docker (порт 8083)'
elif use_postgres:
deployment_mode = 'PostgreSQL (порт 8082)'
else:
deployment_mode = 'SQLite (порт 8081)'

if len(sys.argv) > 1 and '--generate-script' in sys.argv:
print(f" Генерация скрипта с переменными окружения для {deployment_mode}...")
script_path = generate_export_script(use_postgres, use_docker)
print(f" Скрипт создан: {script_path}")
print(" Для использования выполните: source <имя_скрипта>.sh")
else:
print(f" Установка переменных окружения Airflow с абсолютными путями - {deployment_mode}")
print("=" * 70)
set_environment_variables(use_postgres, use_docker)

# Также генерируем скрипт
print(f"\n Генерация скрипта для bash - {deployment_mode}...")
script_path = generate_export_script(use_postgres, use_docker)
print(f" Создан скрипт: {script_path}")
print(" Для применения переменных в bash выполните: source <имя_скрипта>.sh")
print("")
print(" Использование:")
print(" python set_absolute_paths_env.py # SQLite (порт 8081)")
print(" python set_absolute_paths_env.py --postgres # PostgreSQL (порт 8082)")
print(" python set_absolute_paths_env.py --docker # Docker (порт 8083)")

if __name__ == "__main__":
main()
