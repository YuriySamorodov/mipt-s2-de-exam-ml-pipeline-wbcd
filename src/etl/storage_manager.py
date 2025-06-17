"""
Модуль для сохранения результатов в облачное хранилище или локально.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pathlib import Path
import shutil
import zipfile
import sys
import sqlite3
import tempfile

# Добавляем корневую папку в путь для импорта конфигурации
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
from config.config_utils import Config, get_logger, ensure_dir
except ImportError:
def get_logger(name: str):
logging.basicConfig(level=logging.INFO)
return logging.getLogger(name)

# Опциональные импорты для облачных хранилищ
try:
from google.cloud import storage as gcs
GCS_AVAILABLE = True
except ImportError:
GCS_AVAILABLE = False

try:
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
AWS_AVAILABLE = True
except ImportError:
AWS_AVAILABLE = False

# Опциональные импорты для баз данных
try:
import psycopg2
import pandas as pd
DB_AVAILABLE = True
except ImportError:
try:
import pandas as pd
DB_AVAILABLE = True
except ImportError:
DB_AVAILABLE = False

try:
import sqlalchemy
from sqlalchemy import create_engine, text
SQLALCHEMY_AVAILABLE = True
except ImportError:
SQLALCHEMY_AVAILABLE = False


logger = get_logger(__name__)


class StorageManager:
"""Класс для управления сохранением результатов в различные хранилища."""

def __init__(self, config: Optional[Config] = None):
"""
Инициализация менеджера хранилища.

Args:
config: Объект конфигурации
"""
self.config = config or Config()
self.storage_config = self.config.get_storage_config()

# Инициализация клиентов облачных хранилищ
self.gcs_client = None
self.s3_client = None
self.db_engine = None
self.db_connection = None

self._init_cloud_clients()
self._init_database_connection()

def _init_database_connection(self):
"""Инициализирует подключение к базе данных."""
if not SQLALCHEMY_AVAILABLE:
logger.info("SQLAlchemy не установлен, база данных недоступна")
return

try:
db_config = self.storage_config.get("database", {})
db_type = db_config.get("type", "sqlite")

if db_type == "sqlite":
db_path = db_config.get("path", "ml_pipeline.db")
connection_string = f"sqlite:///{db_path}"

elif db_type == "postgresql":
host = db_config.get("host", "localhost")
port = db_config.get("port", 5432)
database = db_config.get("database", "ml_pipeline")
username = os.getenv("DB_USERNAME", db_config.get("username"))
password = os.getenv("DB_PASSWORD", db_config.get("password"))

if username and password:
connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
else:
logger.warning("Не указаны credentials для PostgreSQL")
return

elif db_type == "mysql":
host = db_config.get("host", "localhost")
port = db_config.get("port", 3306)
database = db_config.get("database", "ml_pipeline")
username = os.getenv("DB_USERNAME", db_config.get("username"))
password = os.getenv("DB_PASSWORD", db_config.get("password"))

if username and password:
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
else:
logger.warning("Не указаны credentials для MySQL")
return
else:
logger.warning(f"Неподдерживаемый тип базы данных: {db_type}")
return

self.db_engine = create_engine(connection_string, echo=False)
logger.info(f"База данных инициализирована: {db_type}")

except Exception as e:
logger.warning(f"Ошибка инициализации базы данных: {str(e)}")

def _init_cloud_clients(self):
"""Инициализирует клиенты облачных хранилищ."""
logger.info("Начинаем инициализацию облачных клиентов...")

# Google Cloud Storage
if GCS_AVAILABLE:
try:
logger.info("Инициализируем GCS клиент...")
credentials_path = self.storage_config.get("gcs", {}).get("credentials_path")
if credentials_path and os.path.exists(credentials_path):
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
self.gcs_client = gcs.Client()
logger.info("Google Cloud Storage клиент инициализирован")
elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
self.gcs_client = gcs.Client()
logger.info("Google Cloud Storage клиент инициализирован через переменную окружения")
else:
logger.info("GCS credentials не найдены, пропускаем инициализацию")
except Exception as e:
logger.warning(f"Ошибка инициализации GCS клиента: {str(e)}")

# AWS S3 - отключаем для избежания зависания
logger.info("Проверяем AWS S3...")
if AWS_AVAILABLE:
try:
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

if aws_access_key and aws_secret_key:
logger.info("AWS credentials найдены, но S3 клиент отключен для стабильности Airflow")
# Закомментировано для избежания зависания:
# self.s3_client = boto3.client('s3', region_name=aws_region)
# logger.info("AWS S3 клиент инициализирован")
else:
logger.info("AWS credentials не найдены")
except Exception as e:
logger.warning(f"Ошибка инициализации S3 клиента: {str(e)}")

logger.info("Инициализация облачных клиентов завершена")

def save_to_local(self, data: Any, file_path: str, data_type: str = "json") -> bool:
"""
Сохраняет данные в локальное хранилище.

Args:
data: Данные для сохранения
file_path: Путь к файлу
data_type: Тип данных (json, text, binary)

Returns:
True если успешно, False в противном случае
"""
try:
ensure_dir(os.path.dirname(file_path))

if data_type == "json":
with open(file_path, 'w', encoding='utf-8') as f:
json.dump(data, f, indent=2, ensure_ascii=False, default=str)
elif data_type == "text":
with open(file_path, 'w', encoding='utf-8') as f:
f.write(str(data))
elif data_type == "binary":
with open(file_path, 'wb') as f:
f.write(data)
else:
logger.error(f"Неподдерживаемый тип данных: {data_type}")
return False

logger.info(f"Данные сохранены локально: {file_path}")
return True

except Exception as e:
logger.error(f"Ошибка сохранения в локальное хранилище: {str(e)}")
return False

def copy_file_to_local(self, source_path: str, destination_path: str) -> bool:
"""
Копирует файл в локальное хранилище.

Args:
source_path: Исходный путь к файлу
destination_path: Путь назначения

Returns:
True если успешно, False в противном случае
"""
try:
ensure_dir(os.path.dirname(destination_path))
shutil.copy2(source_path, destination_path)
logger.info(f"Файл скопирован: {source_path} -> {destination_path}")
return True
except Exception as e:
logger.error(f"Ошибка копирования файла: {str(e)}")
return False

def upload_to_gcs(self, local_file_path: str, gcs_blob_name: str, 
bucket_name: Optional[str] = None) -> bool:
"""
Загружает файл в Google Cloud Storage.

Args:
local_file_path: Путь к локальному файлу
gcs_blob_name: Имя объекта в GCS
bucket_name: Имя bucket (если не указано, берется из конфигурации)

Returns:
True если успешно, False в противном случае
"""
if not self.gcs_client:
logger.error("GCS клиент не инициализирован")
return False

if bucket_name is None:
bucket_name = self.storage_config.get("gcs", {}).get("bucket_name")

if not bucket_name:
logger.error("Не указано имя bucket для GCS")
return False

try:
bucket = self.gcs_client.bucket(bucket_name)
blob = bucket.blob(gcs_blob_name)

blob.upload_from_filename(local_file_path)
logger.info(f"Файл загружен в GCS: {local_file_path} -> gs://{bucket_name}/{gcs_blob_name}")
return True

except Exception as e:
logger.error(f"Ошибка загрузки в GCS: {str(e)}")
return False

def upload_to_s3(self, local_file_path: str, s3_key: str, 
bucket_name: Optional[str] = None) -> bool:
"""
Загружает файл в AWS S3.

Args:
local_file_path: Путь к локальному файлу
s3_key: Ключ объекта в S3
bucket_name: Имя bucket (если не указано, берется из переменной окружения)

Returns:
True если успешно, False в противном случае
"""
if not self.s3_client:
logger.error("S3 клиент не инициализирован")
return False

if bucket_name is None:
bucket_name = os.getenv("AWS_BUCKET_NAME")

if not bucket_name:
logger.error("Не указано имя bucket для S3")
return False

try:
self.s3_client.upload_file(local_file_path, bucket_name, s3_key)
logger.info(f"Файл загружен в S3: {local_file_path} -> s3://{bucket_name}/{s3_key}")
return True

except Exception as e:
logger.error(f"Ошибка загрузки в S3: {str(e)}")
return False

def create_results_archive(self, results_dir: str = "results", 
archive_path: str = None) -> Optional[str]:
"""
Создает архив с результатами работы пайплайна.

Args:
results_dir: Директория с результатами
archive_path: Путь к архиву (если не указан, генерируется автоматически)

Returns:
Путь к созданному архиву или None при ошибке
"""
if archive_path is None:
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archive_path = f"results/ml_pipeline_results_{timestamp}.zip"

try:
ensure_dir(os.path.dirname(archive_path))

logger.info(f"Начинаем создание архива: {archive_path}")

# Список файлов и папок для исключения
exclude_extensions = ['.zip', '.tar.gz', '.tar', '.tmp']
exclude_files = ['__pycache__', '.DS_Store']
exclude_prefixes = ['temp_']

# Максимальный размер файла для включения в архив (100MB)
max_file_size = 100 * 1024 * 1024
files_added = 0

with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
for root, dirs, files in os.walk(results_dir):
# Исключаем папки __pycache__
dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]

for file in files:
file_path = os.path.join(root, file)

# Проверяем размер файла
try:
file_size = os.path.getsize(file_path)
if file_size > max_file_size:
logger.warning(f"Файл {file_path} слишком большой ({file_size} bytes), пропускаем")
continue
except OSError:
continue

# Проверяем файлы для исключения
should_exclude = False

# Проверяем расширения
for ext in exclude_extensions:
if file.endswith(ext):
should_exclude = True
break

# Проверяем имена файлов
if not should_exclude:
for exclude_name in exclude_files:
if exclude_name in file:
should_exclude = True
break

# Проверяем префиксы
if not should_exclude:
for prefix in exclude_prefixes:
if file.startswith(prefix):
should_exclude = True
break

if should_exclude:
continue

try:
arcname = os.path.relpath(file_path, os.path.dirname(results_dir))
zipf.write(file_path, arcname)
files_added += 1

# Логируем прогресс каждые 10 файлов
if files_added % 10 == 0:
logger.info(f"Добавлено файлов в архив: {files_added}")
except Exception as e:
logger.warning(f"Не удалось добавить файл {file_path} в архив: {e}")
continue

logger.info(f"Архив результатов создан: {archive_path} (всего файлов: {files_added})")
return archive_path

except Exception as e:
logger.error(f"Ошибка создания архива: {str(e)}")
return None

def save_pipeline_results(self, results: Dict[str, Any], 
model_path: Optional[str] = None,
metrics_path: Optional[str] = None,
upload_to_cloud: bool = False) -> Dict[str, bool]:
"""
Сохраняет все результаты пайплайна.

Args:
results: Словарь с результатами
model_path: Путь к модели (должен быть строкой)
metrics_path: Путь к метрикам (должен быть строкой)
upload_to_cloud: Загружать ли в облачное хранилище

Returns:
Словарь с результатами операций сохранения

Raises:
TypeError: Если model_path или metrics_path не являются строками
"""
logger.info("Начало сохранения результатов пайплайна")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_results = {
"local_save": False,
"gcs_upload": False,
"s3_upload": False,
"archive_created": False
}

# Сохраняем результаты локально
local_results_path = f"results/pipeline_results_{timestamp}.json"
save_results["local_save"] = self.save_to_local(results, local_results_path)

# Копируем важные файлы в итоговую директорию
files_to_save = []

# Проверяем, что model_path является строкой перед использованием
if model_path and isinstance(model_path, str) and os.path.exists(model_path):
dest_model_path = f"results/final_model_{timestamp}.joblib"
if self.copy_file_to_local(model_path, dest_model_path):
files_to_save.append(dest_model_path)
elif model_path and not isinstance(model_path, str):
logger.warning(f"model_path должен быть строкой, получен: {type(model_path)} - {model_path}")

# Проверяем, что metrics_path является строкой перед использованием
if metrics_path and isinstance(metrics_path, str) and os.path.exists(metrics_path):
dest_metrics_path = f"results/final_metrics_{timestamp}.json"
if self.copy_file_to_local(metrics_path, dest_metrics_path):
files_to_save.append(dest_metrics_path)
elif metrics_path and not isinstance(metrics_path, str):
logger.warning(f"metrics_path должен быть строкой, получен: {type(metrics_path)} - {metrics_path}")

# Создаем архив с результатами
archive_path = self.create_results_archive()
if archive_path:
save_results["archive_created"] = True
files_to_save.append(archive_path)

# Загружаем в облачные хранилища (если требуется)
if upload_to_cloud:
for file_path in files_to_save:
if not os.path.exists(file_path):
continue

file_name = os.path.basename(file_path)
cloud_path = f"ml-pipeline/{timestamp}/{file_name}"

# Загружаем в GCS
if self.gcs_client:
gcs_success = self.upload_to_gcs(file_path, cloud_path)
save_results["gcs_upload"] = save_results.get("gcs_upload", False) or gcs_success

# Загружаем в S3
if self.s3_client:
s3_success = self.upload_to_s3(file_path, cloud_path)
save_results["s3_upload"] = save_results.get("s3_upload", False) or s3_success

# Сохраняем сводку операций
summary = {
"timestamp": timestamp,
"files_saved": files_to_save,
"save_operations": save_results,
"local_results_path": local_results_path if save_results["local_save"] else None,
"archive_path": archive_path if save_results["archive_created"] else None
}

summary_path = f"results/save_summary_{timestamp}.json"
self.save_to_local(summary, summary_path)

logger.info("Сохранение результатов пайплайна завершено")
logger.info(f"Результаты операций: {save_results}")

return save_results

def cleanup_old_results(self, results_dir: str = "results", 
max_age_days: int = 30) -> int:
"""
Очищает старые результаты.

Args:
results_dir: Директория с результатами
max_age_days: Максимальный возраст файлов в днях

Returns:
Количество удаленных файлов
"""
logger.info(f"Очистка старых результатов (старше {max_age_days} дней)")

if not os.path.exists(results_dir):
logger.info("Директория результатов не существует")
return 0

deleted_count = 0
current_time = datetime.now().timestamp()
max_age_seconds = max_age_days * 24 * 60 * 60

try:
for root, dirs, files in os.walk(results_dir):
for file in files:
file_path = os.path.join(root, file)
file_age = current_time - os.path.getmtime(file_path)

if file_age > max_age_seconds:
os.remove(file_path)
deleted_count += 1
logger.debug(f"Удален старый файл: {file_path}")

except Exception as e:
logger.error(f"Ошибка при очистке старых результатов: {str(e)}")

logger.info(f"Очистка завершена. Удалено файлов: {deleted_count}")
return deleted_count

def get_storage_info(self) -> Dict[str, Any]:
"""
Получает информацию о доступных хранилищах.

Returns:
Словарь с информацией о хранилищах
"""
info = {
"local_storage": {
"available": True,
"path": os.path.abspath("results")
},
"gcs_storage": {
"available": self.gcs_client is not None,
"client_initialized": self.gcs_client is not None,
"bucket_name": self.storage_config.get("gcs", {}).get("bucket_name")
},
"s3_storage": {
"available": self.s3_client is not None,
"client_initialized": self.s3_client is not None,
"bucket_name": os.getenv("AWS_BUCKET_NAME")
}
}

return info

def create_tables_schema(self):
"""Создает схему таблиц в базе данных."""
if not self.db_engine:
logger.warning("База данных не инициализирована")
return False

try:
# Создаем таблицы если их нет
with self.db_engine.connect() as connection:
# Таблица для хранения данных
connection.execute(text("""
CREATE TABLE IF NOT EXISTS ml_data (
id INTEGER PRIMARY KEY,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
feature_data TEXT,
target_value REAL,
data_version TEXT,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""))

# Таблица для результатов экспериментов
connection.execute(text("""
CREATE TABLE IF NOT EXISTS experiment_results (
id INTEGER PRIMARY KEY,
experiment_name TEXT,
model_type TEXT,
parameters TEXT,
metrics TEXT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""))

# Таблица для мониторинга качества данных
connection.execute(text("""
CREATE TABLE IF NOT EXISTS data_quality_reports (
id INTEGER PRIMARY KEY,
report_data TEXT,
quality_score REAL,
issues_count INTEGER,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""))

logger.info("Схема таблиц создана успешно")
return True

except Exception as e:
logger.error(f"Ошибка создания схемы таблиц: {str(e)}")
return False

def save_data_to_db(self, data: Any, table_name: str = "ml_data") -> bool:
"""
Сохраняет данные в базу данных.

Args:
data: Данные для сохранения (DataFrame или dict)
table_name: Имя таблицы

Returns:
True если успешно, False в противном случае
"""
if not self.db_engine:
logger.warning("База данных не инициализирована")
return False

try:
import pandas as pd

if isinstance(data, pd.DataFrame):
# Сохраняем DataFrame напрямую
data.to_sql(table_name, self.db_engine, if_exists='append', index=False)
logger.info(f"DataFrame сохранен в таблицу {table_name}")
return True

elif isinstance(data, dict):
# Конвертируем dict в DataFrame и сохраняем
df = pd.DataFrame([data])
df.to_sql(table_name, self.db_engine, if_exists='append', index=False)
logger.info(f"Данные сохранены в таблицу {table_name}")
return True

else:
logger.error(f"Неподдерживаемый тип данных: {type(data)}")
return False

except Exception as e:
logger.error(f"Ошибка сохранения данных в БД: {str(e)}")
return False

def load_data_from_db(self, table_name: str = "ml_data", limit: int = None) -> Optional[Any]:
"""
Загружает данные из базы данных.

Args:
table_name: Имя таблицы
limit: Ограничение количества записей

Returns:
DataFrame или None при ошибке
"""
if not self.db_engine:
logger.warning("База данных не инициализирована")
return None

try:
import pandas as pd

query = f"SELECT * FROM {table_name}"
if limit:
query += f" LIMIT {limit}"

df = pd.read_sql(query, self.db_engine)
logger.info(f"Загружено {len(df)} записей из таблицы {table_name}")
return df

except Exception as e:
logger.error(f"Ошибка загрузки данных из БД: {str(e)}")
return None

def save_experiment_results(self, experiment_name: str, model_type: str, 
parameters: Dict[str, Any], metrics: Dict[str, float]) -> bool:
"""
Сохраняет результаты эксперимента в базу данных.

Args:
experiment_name: Название эксперимента
model_type: Тип модели
parameters: Параметры модели
metrics: Метрики модели

Returns:
True если успешно, False в противном случае
"""
if not self.db_engine:
logger.warning("База данных не инициализирована")
return False

try:
experiment_data = {
'experiment_name': experiment_name,
'model_type': model_type,
'parameters': json.dumps(parameters),
'metrics': json.dumps(metrics),
'timestamp': datetime.now().isoformat()
}

return self.save_data_to_db(experiment_data, 'experiment_results')

except Exception as e:
logger.error(f"Ошибка сохранения результатов эксперимента: {str(e)}")
return False

def get_database_info(self) -> Dict[str, Any]:
"""
Получает информацию о базе данных.

Returns:
Словарь с информацией о базе данных
"""
info = {
"database_available": self.db_engine is not None,
"connection_string": str(self.db_engine.url) if self.db_engine else None,
"tables": []
}

if self.db_engine:
try:
with self.db_engine.connect() as connection:
# Получаем список таблиц (для SQLite)
result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
info["tables"] = [row[0] for row in result.fetchall()]
except Exception as e:
logger.error(f"Ошибка получения информации о БД: {str(e)}")
info["error"] = str(e)

return info


def main():
"""Главная функция для тестирования модуля."""
try:
# Создаем менеджер хранилища
storage_manager = StorageManager()

# Получаем информацию о хранилищах
storage_info = storage_manager.get_storage_info()
print("Информация о хранилищах:")
print(json.dumps(storage_info, indent=2, ensure_ascii=False))

# Тестируем сохранение данных
test_data = {
"test": "Тестовые данные",
"timestamp": datetime.now().isoformat(),
"metrics": {"accuracy": 0.95, "f1_score": 0.92}
}

# Сохраняем тестовые результаты
results = storage_manager.save_pipeline_results(
test_data,
upload_to_cloud=False # Отключаем загрузку в облако для теста
)

print(f"Результаты сохранения: {results}")

# Очищаем старые результаты (тест)
deleted_count = storage_manager.cleanup_old_results(max_age_days=0) # Удаляем все для теста
print(f"Удалено файлов при очистке: {deleted_count}")

return storage_manager

except Exception as e:
logger.error(f"Ошибка в main: {str(e)}")
raise


if __name__ == "__main__":
main()
