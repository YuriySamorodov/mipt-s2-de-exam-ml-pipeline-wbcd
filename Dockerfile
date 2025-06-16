# Dockerfile для ML Pipeline проекта
FROM python:3.9-slim

# Метаданные
LABEL maintainer="Самородов Юрий Сергеевич, МФТИ"
LABEL description="ML Pipeline для диагностики рака молочной железы"
LABEL version="1.0.0"

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash mluser

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p data results/models results/metrics results/preprocessors logs && \
    chown -R mluser:mluser /app

# Переключение на непривилегированного пользователя
USER mluser

# Установка переменных окружения
ENV CONFIG_PATH=config/config.yaml \
    LOG_LEVEL=INFO \
    ENVIRONMENT=production

# Порт для веб-сервисов (если будут добавлены)
EXPOSE 8000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "from config.config_utils import Config; Config()" || exit 1

# Точка входа по умолчанию
CMD ["python", "-c", "from etl.data_loader import main; from etl.data_preprocessor import main as preprocess_main; from etl.model_trainer import main as train_main; from etl.metrics_calculator import main as metrics_main; from etl.storage_manager import main as storage_main; main(); preprocess_main(); train_main(); metrics_main(); storage_main()"]
