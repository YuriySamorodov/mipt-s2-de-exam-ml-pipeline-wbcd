# Makefile для управления ML пайплайном
# Автор: Самородов Юрий Сергеевич, МФТИ
# Дата: 2025-06-14
# Версия: 1.0
# Описание: Этот Makefile автоматизирует процессы установки, настройки, тестирования и запуска ML пайплайна для диагностики рака молочной железы.
# Использование:
#   make install          - Установка зависимостей
#   make setup            - Первоначальная настройка проекта
#   make test             - Запуск тестов
#   make run-pipeline     - Запуск полного пайплайна локально
#   make run-components   - Запуск отдельных компонентов пайплайна
#   make clean            - Очистка временных файлов
#   make lint             - Проверка кода линтерами
#   make format           - Форматирование кода
#   make airflow-init     - Инициализация Airflow
#   make airflow-start    - Запуск Airflow
#   make airflow-stop     - Остановка Airflow
#   make docker-build     - Сборка Docker образа
#   make docker-run       - Запуск в Docker контейнере
#   make archive          - Создание архива проекта для GitHub
#   make report           - Генерация отчета о проекте
#   make demo             - Быстрый старт для демонстрации
#   make dev-install      - Установка в режиме разработки
#   make docs             - Создание документации
#   make quality          - Проверка качества кода
#   make production-ready - Подготовка проекта к продакшену
#   make env-help         - Справка по переменным окружения
#   make check-config     - Проверка конфигурации
#   make airflow-test     - Тест Airflow DAG
#   make airflow-run-task - Запуск конкретной задачи в Airflow
#   make install          - Установка всех зависимостей
#   make setup            - Создание виртуального окружения и установка зависимостей
#   make test             - Запуск тестов
#   make run-pipeline     - Запуск полного пайплайна
#   make run-components   - Запуск отдельных компонентов пайплайна
#   make clean            - Очистка временных файлов
#   make lint             - Проверка кода линтерами
#   make format           - Форматирование кода
#   make airflow-init     - Инициализация Airflow
#   make airflow-start    - Запуск Airflow
#   make airflow-stop     - Остановка Airflow
#   make docker-build     - Сборка Docker образа
#   make docker-run       - Запуск в Docker контейнере
#   make archive          - Создание архива проекта для GitHub
#   make report           - Генерация отчета о проекте
#   make demo             - Быстрый старт для демонстрации
#   make dev-install      - Установка в режиме разработки
#   make docs             - Создание документации	
# Проект: Диагностика рака молочной железы

.PHONY: help install setup test run-pipeline clean lint format docker airflow-init airflow-start airflow-stop

# Переменные
PYTHON := python3
PIP := pip3
VENV := venv
AIRFLOW_HOME := ./airflow
CONFIG_FILE := config/config.yaml
LOG_LEVEL := INFO

# По умолчанию показываем помощь
help:
	@echo "ML Pipeline для диагностики рака молочной железы"
	@echo ""
	@echo "Доступные команды:"
	@echo "  install         - Установка всех зависимостей"
	@echo "  setup           - Первоначальная настройка проекта"
	@echo "  test            - Запуск тестов"
	@echo "  run-pipeline    - Запуск полного пайплайна локально"
	@echo "  run-components  - Запуск отдельных компонентов пайплайна"
	@echo "  clean           - Очистка временных файлов"
	@echo "  lint            - Проверка кода линтерами"
	@echo "  format          - Форматирование кода"
	@echo "  airflow-init    - Инициализация Airflow"
	@echo "  airflow-start   - Запуск Airflow"
	@echo "  airflow-stop    - Остановка Airflow"
	@echo "  docker-build    - Сборка Docker образа"
	@echo "  docker-run      - Запуск в Docker контейнере"
	@echo "  archive         - Создание архива проекта для GitHub"
	@echo ""

# Установка зависимостей
install:
	@echo "Установка зависимостей..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Зависимости установлены"

# Создание виртуального окружения и установка зависимостей
setup: 
	@echo "Настройка проекта..."
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip
	./$(VENV)/bin/pip install -r requirements.txt
	@echo "Создание необходимых директорий..."
	mkdir -p data results/models results/metrics results/preprocessors logs
	@echo "Копирование примера конфигурации..."
	cp .env.example .env
	@echo "Проект настроен!"
	@echo "Не забудьте:"
	@echo "   - Отредактировать .env файл"
	@echo "   - Проверить config/config.yaml"
	@echo "   - Активировать виртуальное окружение: source $(VENV)/bin/activate"

# Запуск тестов
test:
	@echo "Запуск тестов..."
	$(PYTHON) -m pytest tests/ -v --cov=etl --cov-report=html
	@echo "Тесты завершены"

# Запуск отдельных компонентов
run-components:
	@echo "Тестирование загрузки данных..."
	$(PYTHON) etl/data_loader.py
	@echo ""
	@echo "Тестирование предобработки..."
	$(PYTHON) etl/data_preprocessor.py
	@echo ""
	@echo "Тестирование обучения модели..."
	$(PYTHON) etl/model_trainer.py
	@echo ""
	@echo "Тестирование расчета метрик..."
	$(PYTHON) etl/metrics_calculator.py
	@echo ""
	@echo "Тестирование сохранения результатов..."
	$(PYTHON) etl/storage_manager.py

# Запуск полного пайплайна
run-pipeline:
	@echo "Запуск полного ML пайплайна..."
	@echo "Этап 1: Загрузка данных"
	$(PYTHON) etl/data_loader.py
	@echo "Этап 2: Предобработка данных"
	$(PYTHON) etl/data_preprocessor.py
	@echo "Этап 3: Обучение модели"
	$(PYTHON) etl/model_trainer.py
	@echo "Этап 4: Оценка модели"
	$(PYTHON) etl/metrics_calculator.py
	@echo "Этап 5: Сохранение результатов"
	$(PYTHON) etl/storage_manager.py
	@echo "Пайплайн завершен успешно!"
	@echo "Результаты сохранены в папке results/"

# Очистка временных файлов
clean:
	@echo "Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf logs/*.log
	@echo "Очистка завершена"

# Линтинг кода
lint:
	@echo "Проверка кода линтерами..."
	flake8 etl/ dags/ config/ --max-line-length=100 --ignore=E203,W503
	mypy etl/ --ignore-missing-imports
	@echo "Линтинг завершен"

# Форматирование кода
format:
	@echo "Форматирование кода..."
	black etl/ dags/ config/ --line-length=100
	@echo "Форматирование завершено"

# Инициализация Airflow
airflow-init:
	@echo "Инициализация Apache Airflow..."
	export AIRFLOW_HOME=$(AIRFLOW_HOME) && \
	airflow db init && \
	airflow users create \
		--username admin \
		--password admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com
	@echo "Airflow инициализирован"
	@echo "Пользователь: admin, Пароль: admin"

# Запуск Airflow
airflow-start:
	@echo "Запуск Apache Airflow..."
	export AIRFLOW_HOME=$(AIRFLOW_HOME) && \
	export AIRFLOW__CORE__DAGS_FOLDER=$(PWD)/dags && \
	export AIRFLOW__CORE__LOGS_FOLDER=$(PWD)/logs && \
	airflow webserver --port 8080 --daemon && \
	airflow scheduler --daemon
	@echo "Airflow запущен!"
	@echo "Web UI: http://localhost:8080"

# Остановка Airflow
airflow-stop:
	@echo "Остановка Apache Airflow..."
	pkill -f "airflow webserver" || true
	pkill -f "airflow scheduler" || true
	@echo "Airflow остановлен"

# Тест Airflow DAG
airflow-test:
	@echo "Тестирование Airflow DAG..."
	export AIRFLOW_HOME=$(AIRFLOW_HOME) && \
	airflow dags test breast_cancer_ml_pipeline $(shell date +%Y-%m-%d)
	@echo "Тест DAG завершен"

# Запуск конкретной задачи в Airflow
airflow-run-task:
	@echo "Запуск задачи $(TASK) в DAG..."
	export AIRFLOW_HOME=$(AIRFLOW_HOME) && \
	airflow tasks test breast_cancer_ml_pipeline $(TASK) $(shell date +%Y-%m-%d)

# Сборка Docker образа
docker-build:
	@echo "Сборка Docker образа..."
	docker build -t ml-pipeline:latest .
	@echo "Docker образ собран"

# Запуск в Docker
docker-run:
	@echo "Запуск в Docker контейнере..."
	docker run --rm -v $(PWD)/data:/app/data -v $(PWD)/results:/app/results ml-pipeline:latest
	@echo "Выполнение в Docker завершено"

# Создание архива для GitHub
archive:
	@echo "Создание архива проекта..."
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S) && \
	ARCHIVE_NAME="ml-pipeline-breast-cancer-$$TIMESTAMP.tar.gz" && \
	tar -czf $$ARCHIVE_NAME \
		--exclude='.git' \
		--exclude='venv' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='.pytest_cache' \
		--exclude='htmlcov' \
		--exclude='logs/*.log' \
		--exclude='results/models/*.joblib' \
		--exclude='results/models/*.pkl' \
		. && \
	echo "Архив создан: $$ARCHIVE_NAME"

# Проверка конфигурации
check-config:
	@echo "Проверка конфигурации..."
	$(PYTHON) -c "from config.config_utils import Config; c = Config(); print('Конфигурация корректна')"

# Генерация отчета о проекте
report:
	@echo "Генерация отчета о проекте..."
	@echo "Структура проекта:" > PROJECT_REPORT.md
	@echo "\`\`\`" >> PROJECT_REPORT.md
	@tree -I '__pycache__|*.pyc|venv|.git' >> PROJECT_REPORT.md 2>/dev/null || find . -type d -name '__pycache__' -prune -o -type f -name '*.pyc' -prune -o -name 'venv' -prune -o -name '.git' -prune -o -type f -print | head -20 >> PROJECT_REPORT.md
	@echo "\`\`\`" >> PROJECT_REPORT.md
	@echo "" >> PROJECT_REPORT.md
	@echo "Размер файлов:" >> PROJECT_REPORT.md
	@du -sh * | grep -v venv >> PROJECT_REPORT.md
	@echo "Отчет создан: PROJECT_REPORT.md"

# Быстрый старт для демонстрации
demo-simple:
	@echo "Демонстрация ML пайплайна..."
	@echo "1. Проверка конфигурации..."
	@$(MAKE) check-config
	@echo "2. Тестирование компонентов..."
	@$(MAKE) run-components
	@echo "3. Запуск полного пайплайна..."
	@$(MAKE) run-pipeline
	@echo "Демонстрация завершена!"
	@echo "Результаты доступны в папке results/"

# Демонстрация улучшенных возможностей
demo:
	@echo "Запуск демонстрации пайплайна..."
	python demo_pipeline.py

# Проверка качества данных
quality-check:
	@echo "Проверка качества данных..."
	python -c "from etl.data_loader import DataLoader; from etl.data_quality_controller import DataQualityController; loader = DataLoader(); quality = DataQualityController(); df = loader.load_data('data/wdbc.data.csv'); results = quality.run_comprehensive_checks(df); print(f'Балл качества: {results[\"overall_score\"]:.1f}/100')"

# Feature engineering демо
feature-engineering:
	@echo "Демонстрация feature engineering..."
	python -c "from etl.data_loader import DataLoader; from etl.data_preprocessor import DataPreprocessor; loader = DataLoader(); preprocessor = DataPreprocessor(); df = loader.load_data('data/wdbc.data.csv'); df_clean = preprocessor.clean_data(df); df_eng = preprocessor.create_feature_engineering(df_clean); print(f'Создано признаков: {len(preprocessor.engineered_features)}')"

# Инициализация базы данных
init-db:
	@echo "Инициализация базы данных..."
	python -c "from etl.storage_manager import StorageManager; storage = StorageManager(); print('База данных инициализирована' if storage.db_engine else 'База данных не инициализирована')"

# Проверка дрейфа данных
drift-check:
	@echo "Проверка дрейфа данных..."
	python -c "from etl.data_loader import DataLoader; import pandas as pd; loader = DataLoader(); df1 = loader.load_data('data/wdbc.data.csv'); df2 = df1.copy(); df2.iloc[:, 2:5] *= 1.1; drift = loader.detect_data_drift(df1, df2); print(f'Дрейф обнаружен: {drift[\"summary\"][\"drift_detected\"]}')"

# Установка дополнительных зависимостей
install-all:
	@echo "Установка дополнительных зависимостей..."
	pip install scipy sqlalchemy psycopg2-binary pymysql plotly imbalanced-learn

# Комплексный тест пайплайна
test-all: install-all quality-check feature-engineering init-db demo
	@echo "Все компоненты протестированы успешно!"

# Проверка качества кода
quality:
	@echo "Проверка качества кода..."
	@$(MAKE) lint
	@$(MAKE) format
	@$(MAKE) test
	@echo "Проверка качества завершена"

# Подготовка к продакшену
production-ready:
	@echo "Подготовка к продакшену..."
	@$(MAKE) quality
	@$(MAKE) clean
	@$(MAKE) run-pipeline
	@$(MAKE) archive
	@echo "Проект готов к продакшену!"

# Справка по переменным окружения
env-help:
	@echo "Переменные окружения:"
	@echo "  CONFIG_PATH            - Путь к файлу конфигурации"
	@echo "  LOG_LEVEL              - Уровень логирования"
	@echo "  AIRFLOW_HOME           - Домашняя папка Airflow"
	@echo "  GOOGLE_APPLICATION_CREDENTIALS - Путь к GCS credentials"
	@echo "  AWS_ACCESS_KEY_ID      - AWS Access Key"
	@echo "  AWS_SECRET_ACCESS_KEY  - AWS Secret Key"
	@echo ""
	@echo "Скопируйте .env.example в .env и настройте значения"
