#!/usr/bin/env python3
"""
Скрипт для программного формирования абсолютных путей в конфигурации Airflow.
Этот скрипт обеспечивает корректное формирование всех путей к файлам и базе данных.
"""

import os
import sys
import configparser
from pathlib import Path

def setup_airflow_paths():
"""Настройка абсолютных путей для Airflow"""

# Определяем базовые пути
current_dir = Path(__file__).parent.absolute()
project_dir = current_dir.parent.parent # Поднимаемся на 2 уровня вверх к корню проекта

# Формируем абсолютные пути программно
airflow_home = project_dir / "airflow"
dags_folder = project_dir / "dags"
plugins_folder = project_dir / "plugins"
logs_folder = project_dir / "logs"

# Создаем директории если они не существуют
airflow_home.mkdir(exist_ok=True)
dags_folder.mkdir(exist_ok=True)
plugins_folder.mkdir(exist_ok=True)
logs_folder.mkdir(exist_ok=True)

# Формируем абсолютный путь к базе данных SQLite
sqlite_db_path = airflow_home / "airflow.db"
sql_alchemy_conn_sqlite = f"sqlite:///{sqlite_db_path.absolute()}"

# Формируем абсолютный путь для PostgreSQL (если используется)
# В случае PostgreSQL база данных находится на сервере, но можем указать путь к сокету
postgres_conn = "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"

print(" Формирование абсолютных путей для Airflow...")
print(f" Директория проекта: {project_dir}")
print(f" AIRFLOW_HOME: {airflow_home}")
print(f" DAGs: {dags_folder}")
print(f" Plugins: {plugins_folder}")
print(f" Logs: {logs_folder}")
print(f" SQLite DB: {sqlite_db_path}")

# Настраиваем переменные окружения
os.environ['AIRFLOW_HOME'] = str(airflow_home)
os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = str(dags_folder)
os.environ['AIRFLOW__CORE__PLUGINS_FOLDER'] = str(plugins_folder)
os.environ['AIRFLOW__LOGGING__BASE_LOG_FOLDER'] = str(logs_folder)
os.environ['AIRFLOW__DATABASE__SQL_ALCHEMY_CONN'] = sql_alchemy_conn_sqlite

return {
'project_dir': str(project_dir),
'airflow_home': str(airflow_home),
'dags_folder': str(dags_folder),
'plugins_folder': str(plugins_folder),
'logs_folder': str(logs_folder),
'sqlite_db_path': str(sqlite_db_path),
'sql_alchemy_conn_sqlite': sql_alchemy_conn_sqlite,
'sql_alchemy_conn_postgres': postgres_conn
}

def create_airflow_config(paths, use_postgres=False, use_docker=False):
"""Создание файла airflow.cfg с абсолютными путями"""

config_path = Path(paths['airflow_home']) / 'airflow.cfg'

# Определяем порт в зависимости от варианта развертывания
if use_docker:
port = '8083'
deployment_type = 'Docker'
elif use_postgres:
port = '8082'
deployment_type = 'PostgreSQL'
else:
port = '8081'
deployment_type = 'SQLite'

# Базовая конфигурация
config = configparser.ConfigParser()

# Секция [core]
config['core'] = {
'dags_folder': paths['dags_folder'],
'hostname_callable': 'socket.getfqdn',
'default_timezone': 'UTC',
'executor': 'SequentialExecutor' if not (use_postgres or use_docker) else 'LocalExecutor',
'parallelism': '32',
'max_active_tasks_per_dag': '16',
'dags_are_paused_at_creation': 'True',
'max_active_runs_per_dag': '16',
'load_examples': 'False',
'plugins_folder': paths['plugins_folder'],
'fernet_key': '',
'donot_pickle': 'True',
'dagbag_import_timeout': '30',
'task_runner': 'StandardTaskRunner',
'default_impersonation': '',
'security': '',
'unit_test_mode': 'False',
'enable_xcom_pickling': 'True',
'killed_task_cleanup_time': '60',
'dag_discovery_safe_mode': 'True',
'default_task_retries': '0',
'min_serialized_dag_update_interval': '30',
'store_serialized_dags': 'True',
'store_dag_code': 'True',
'min_serialized_dag_fetch_interval': '10',
'max_num_rendered_ti_fields_per_task': '30',
'check_slas': 'False',
'xcom_backend': 'airflow.models.xcom.BaseXCom',
'lazy_load_plugins': 'True',
'lazy_discover_providers': 'True'
}

# Секция [database]
database_conn = paths['sql_alchemy_conn_postgres'] if (use_postgres or use_docker) else paths['sql_alchemy_conn_sqlite']
config['database'] = {
'sql_alchemy_conn': database_conn,
'sql_engine_encoding': 'utf-8',
'sql_alchemy_pool_enabled': 'True',
'sql_alchemy_pool_size': '5',
'sql_alchemy_max_overflow': '10',
'sql_alchemy_pool_recycle': '1800',
'sql_alchemy_pool_pre_ping': 'True',
'sql_alchemy_schema': '',
'load_default_connections': 'True'
}

# Секция [logging]
config['logging'] = {
'base_log_folder': paths['logs_folder'],
'remote_logging': 'False',
'remote_log_conn_id': '',
'remote_base_log_folder': '',
'encrypt_s3_logs': 'False',
'logging_level': 'INFO',
'fab_logging_level': 'WARN',
'logging_config_class': '',
'colored_console_log': 'True',
'colored_log_format': '[%%(blue)s%%(asctime)s%%(reset)s] {{%%(blue)s%%(filename)s:%%(reset)s%%(lineno)d}} %%(log_color)s%%(levelname)s%%(reset)s - %%(log_color)s%%(message)s%%(reset)s',
'colored_formatter_class': 'airflow.utils.log.colored_log.CustomTTYColoredFormatter',
'log_format': '[%%(asctime)s] {{%%(filename)s:%%(lineno)d}} %%(levelname)s - %%(message)s',
'simple_log_format': '%%(levelname)s - %%(message)s',
'task_log_prefix_template': '',
'log_filename_template': '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log',
'log_processor_filename_template': '{{ filename }}.log',
'dag_processor_manager_log_location': f"{paths['logs_folder']}/dag_processor_manager/dag_processor_manager.log",
'task_log_reader': 'task'
}

# Секция [webserver]
config['webserver'] = {
'base_url': f'http://localhost:{port}',
'default_ui_timezone': 'UTC',
'web_server_host': '0.0.0.0',
'web_server_port': port,
'web_server_ssl_cert': '',
'web_server_ssl_key': '',
'web_server_master_timeout': '120',
'web_server_worker_timeout': '120',
'worker_refresh_batch_size': '1',
'worker_refresh_interval': '6000',
'reload_on_plugin_change': 'False',
'secret_key': 'temporary_key_for_development',
'workers': '4' if (use_postgres or use_docker) else '1',
'worker_class': 'sync',
'access_logfile': '-',
'error_logfile': '-',
'expose_config': 'True',
'expose_hostname': 'True',
'expose_stacktrace': 'True',
'dag_default_view': 'tree',
'dag_orientation': 'LR',
'demo_mode': 'False',
'log_fetch_timeout_sec': '5',
'log_fetch_delay_sec': '2',
'log_auto_tailing_offset': '30',
'log_animation_speed': '1000',
'hide_paused_dags_by_default': 'False',
'page_size': '100',
'navbar_color': '#fff',
'default_dag_run_display_number': '25',
'enable_proxy_fix': 'False',
'proxy_fix_x_for': '1',
'proxy_fix_x_proto': '1',
'proxy_fix_x_host': '1',
'proxy_fix_x_port': '1',
'proxy_fix_x_prefix': '1',
'cookie_secure': 'False',
'cookie_samesite': 'Lax',
'default_wrap': 'False',
'x_frame_enabled': 'True',
'show_recent_stats_for_completed_runs': 'True',
'update_fab_perms': 'True'
}

# Секция [scheduler]
config['scheduler'] = {
'job_heartbeat_sec': '5',
'scheduler_heartbeat_sec': '5',
'run_duration': '-1',
'min_file_process_interval': '0',
'dag_dir_list_interval': '300',
'print_stats_interval': '30',
'pool_metrics_interval': '5.0',
'scheduler_health_check_threshold': '30',
'child_process_log_directory': f"{paths['logs_folder']}/scheduler",
'scheduler_zombie_task_threshold': '300',
'catchup_by_default': 'True',
'max_tis_per_query': '512',
'use_row_level_locking': 'True',
'max_dagruns_to_create_per_loop': '10',
'max_dagruns_per_loop_to_schedule': '20',
'schedule_after_task_execution': 'True',
'parsing_processes': '2' if (use_postgres or use_docker) else '1',
'file_parsing_sort_mode': 'modified_time',
'allow_trigger_in_future': 'False'
}

# Записываем конфигурацию в файл
with open(config_path, 'w') as configfile:
config.write(configfile)

print(f" Создан файл конфигурации: {config_path}")
print(f" База данных: {deployment_type}")
print(f" Исполнитель: {'LocalExecutor' if (use_postgres or use_docker) else 'SequentialExecutor'}")
print(f" Веб-сервер: http://localhost:{port}")

return str(config_path)

def main():
"""Основная функция"""

# Проверяем аргументы командной строки
use_postgres = '--postgres' in sys.argv
use_docker = '--docker' in sys.argv

# Определяем режим развертывания
if use_docker:
deployment_mode = 'Docker (порт 8083)'
port = '8083'
elif use_postgres:
deployment_mode = 'PostgreSQL (порт 8082)'
port = '8082'
else:
deployment_mode = 'SQLite (порт 8081)'
port = '8081'

print(" Настройка конфигурации Airflow с абсолютными путями")
print(f" Режим развертывания: {deployment_mode}")
print("")

# Формируем пути
paths = setup_airflow_paths()

# Создаем конфигурацию
config_path = create_airflow_config(paths, use_postgres, use_docker)

print("")
print(" Настройка завершена успешно!")
print("")
print(" Сводка путей:")
for key, value in paths.items():
if key.startswith('sql_alchemy_conn'):
if ((use_postgres or use_docker) and 'postgres' in key) or (not use_postgres and not use_docker and 'sqlite' in key):
print(f" {key}: {value}")
else:
print(f" {key}: {value}")

print("")
print(" Следующие шаги:")
print(" 1. Запустите скрипт инициализации базы данных")
print(" 2. Используйте обновленные скрипты запуска Airflow")
print(" 3. Все пути теперь формируются программно и являются абсолютными")
print(f" 4. Веб-интерфейс будет доступен на http://localhost:{port}")
print("")
print(" Использование:")
print(" python setup_airflow_config.py # SQLite (порт 8081)")
print(" python setup_airflow_config.py --postgres # PostgreSQL (порт 8082)")
print(" python setup_airflow_config.py --docker # Docker (порт 8083)")

if __name__ == "__main__":
main()
