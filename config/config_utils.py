"""
Утилиты для работы с конфигурацией проекта.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
"""Класс для управления конфигурацией проекта."""

def __init__(self, config_path: str = None):
"""
Инициализация конфигурации.

Args:
config_path: Путь к файлу конфигурации
"""
# Загружаем переменные окружения
load_dotenv()

# Определяем путь к конфигурации
if config_path is None:
config_path = "config/config.yaml"

self.config_path = Path(config_path)
self.config = self._load_config()
self._setup_logging()

def _load_config(self) -> Dict[str, Any]:
"""Загружает конфигурацию из YAML файла."""
try:
with open(self.config_path, 'r', encoding='utf-8') as file:
config = yaml.safe_load(file)
return config
except FileNotFoundError:
raise FileNotFoundError(f"Файл конфигурации не найден: {self.config_path}")
except yaml.YAMLError as e:
raise ValueError(f"Ошибка в файле конфигурации: {e}")

def _setup_logging(self):
"""Настройка логирования."""
log_config = self.config.get("logging", {})
log_level = log_config.get("level", "INFO")
log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(
level=getattr(logging, log_level),
format=log_format,
handlers=[
logging.StreamHandler(),
logging.FileHandler(
os.path.join(log_config.get("log_path", "logs"), "pipeline.log"),
encoding='utf-8'
)
]
)

def get(self, key: str, default=None):
"""
Получить значение из конфигурации.

Args:
key: Ключ в формате "section.subsection.key"
default: Значение по умолчанию

Returns:
Значение из конфигурации или default
"""
keys = key.split('.')
value = self.config

for k in keys:
if isinstance(value, dict) and k in value:
value = value[k]
else:
return default

return value

def get_data_config(self) -> Dict[str, Any]:
"""Получить конфигурацию данных."""
return self.config.get("data", {})

def get_model_config(self) -> Dict[str, Any]:
"""Получить конфигурацию модели."""
return self.config.get("model", {})

def get_storage_config(self) -> Dict[str, Any]:
"""Получить конфигурацию хранилища."""
return self.config.get("storage", {})

def get_airflow_config(self) -> Dict[str, Any]:
"""Получить конфигурацию Airflow."""
return self.config.get("airflow", {})


def get_project_root() -> Path:
"""Получить корневой путь проекта."""
return Path(__file__).parent.parent


def ensure_dir(path: str) -> None:
"""Создать директорию, если она не существует."""
Path(path).mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
"""Получить настроенный логгер."""
return logging.getLogger(name)
