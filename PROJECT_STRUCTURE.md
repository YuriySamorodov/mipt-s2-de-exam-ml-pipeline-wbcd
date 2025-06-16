# Структура проекта ML Pipeline

Этот документ описывает полную структуру проекта автоматизированного пайплайна машинного обучения для диагностики рака молочной железы.

```
ml-pipeline-project/
 dags/ # Apache Airflow DAG файлы
 ml_pipeline_dag.py # Основной DAG пайплайна ML

 etl/ # ETL модули пайплайна
 data_loader.py # Загрузка и анализ данных
 data_preprocessor.py # Предобработка данных
 model_trainer.py # Обучение модели
 metrics_calculator.py # Расчет метрик и оценка
 storage_manager.py # Управление хранилищем

 config/ # Конфигурационные файлы
 config.yaml # Основная конфигурация
 config_utils.py # Утилиты конфигурации

 data/ # Исходные данные
 wdbc.data.csv # Wisconsin Breast Cancer Dataset

 results/ # Результаты работы пайплайна
 models/ # Сохраненные модели
 current_model.joblib # Текущая лучшая модель
 logistic_regression_model_*.joblib # Версионные модели
 metrics/ # Метрики и отчеты
 metrics.json # JSON с метриками
 evaluation_report.md # Отчет об оценке модели
 preprocessors/ # Сохраненные препроцессоры
 scaler.joblib # StandardScaler
 label_encoder.joblib # LabelEncoder
 feature_columns.joblib # Список признаков
 confusion_matrix.png # Матрица ошибок
 roc_curve.png # ROC-кривая
 precision_recall_curve.png # Precision-Recall кривая
 data_analysis.json # Отчет анализа данных
 ml_pipeline_results_*.zip # Архивы результатов

 logs/ # Логи выполнения
 pipeline.log # Основной лог пайплайна
 demo_pipeline.log # Лог демонстрации

 tests/ # Тесты
 conftest.py # Конфигурация pytest
 test_data_loader.py # Тесты загрузчика данных
 test_data_preprocessor.py # Тесты препроцессора
 test_model_trainer.py # Тесты обучения модели
 test_metrics_calculator.py # Тесты расчета метрик
 test_storage_manager.py # Тесты менеджера хранилища

 requirements.txt # Python зависимости
 .env.example # Пример переменных окружения
 .gitignore # Git ignore правила
 Makefile # Команды управления проектом
 Dockerfile # Docker образ
 docker-compose.yml # Docker Compose конфигурация
 airflow_commands.sh # Команды для работы с Airflow
 demo_pipeline.py # Скрипт демонстрации пайплайна
 README.md # Основная документация
 DEPLOYMENT.md # Инструкции по развертыванию
```

## Описание компонентов

### DAG файлы (`dags/`)

**ml_pipeline_dag.py** - Основной DAG для Apache Airflow, содержащий:
- 7 связанных задач (health_check → load_data → preprocess → train → evaluate → save → cleanup)
- Конфигурацию retry и timeout
- Обработку ошибок и логирование
- Передачу данных между задачами через XCom

### ETL модули (`etl/`)

**data_loader.py** - Загрузка и первичный анализ данных:
- Загрузка CSV файла Wisconsin Breast Cancer
- Валидация схемы и качества данных
- Статистический анализ
- Обнаружение аномалий

**data_preprocessor.py** - Предобработка данных:
- Очистка данных (дубликаты, пропуски, выбросы)
- Кодирование целевой переменной
- Разделение train/test
- Нормализация признаков

**model_trainer.py** - Обучение модели:
- Создание LogisticRegression модели
- Кросс-валидация
- Подбор гиперпараметров (GridSearchCV)
- Анализ важности признаков

**metrics_calculator.py** - Расчет метрик:
- Accuracy, Precision, Recall, F1-Score
- ROC AUC, матрица ошибок
- Создание визуализаций
- Генерация отчетов

**storage_manager.py** - Управление хранилищем:
- Локальное сохранение результатов
- Интеграция с Google Cloud Storage
- Интеграция с AWS S3
- Создание архивов, очистка файлов

### Конфигурация (`config/`)

**config.yaml** - Основные настройки:
```yaml
data:
 source_file: "data/wdbc.data.csv"
 test_size: 0.2
 random_state: 42

model:
 type: "LogisticRegression"
 parameters:
 random_state: 42
 max_iter: 1000

storage:
 local:
 results_path: "results/"
 gcs:
 bucket_name: "ml-pipeline-results"

airflow:
 dag_id: "breast_cancer_ml_pipeline"
 retries: 2
 timeout_minutes: 30
```

**config_utils.py** - Утилиты для работы с конфигурацией:
- Загрузка YAML конфигурации
- Управление переменными окружения
- Настройка логирования
- Вспомогательные функции

### Данные (`data/`)

**wdbc.data.csv** - Wisconsin Breast Cancer Diagnostic Dataset:
- 569 образцов (357 доброкачественных, 212 злокачественных)
- 32 признака (ID, диагноз, 30 численных характеристик)
- Каждая запись представляет характеристики клеточных ядер

### Результаты (`results/`)

Структура автоматически создается при выполнении пайплайна:

**models/** - Обученные модели:
- `current_model.joblib` - последняя лучшая модель
- Версионные модели с временными метками
- Метаданные модели в JSON формате

**metrics/** - Метрики и отчеты:
- Численные метрики в JSON
- Markdown отчеты
- CSV файлы с детальными результатами

**preprocessors/** - Сохраненные препроцессоры:
- StandardScaler для нормализации
- LabelEncoder для кодирования
- Список признаков

**Визуализации** - PNG графики:
- Матрица ошибок (абсолютная и нормализованная)
- ROC-кривая с AUC
- Precision-Recall кривая

### Тесты (`tests/`)

Полное покрытие тестами всех ETL модулей:
- Unit тесты для каждого класса и метода
- Mock тесты для внешних зависимостей
- Интеграционные тесты пайплайна
- Тесты валидации данных

### Контейнеризация

**Dockerfile** - Мультистадийная сборка:
- Базовый образ Python 3.9
- Установка системных зависимостей
- Копирование и установка Python пакетов
- Настройка безопасности (non-root user)
- Health check и entry point

**docker-compose.yml** - Полная инфраструктура:
- Apache Airflow (webserver, scheduler, workers)
- PostgreSQL база данных
- Jupyter Notebook для разработки
- Grafana + Prometheus для мониторинга
- Настройка сетей и volumes

### Автоматизация

**Makefile** - 25+ команд для управления:
```bash
make setup # Настройка проекта
make demo # Демонстрация пайплайна
make test # Запуск тестов
make airflow-start # Запуск Airflow
make docker-build # Сборка Docker образа
make quality # Проверка качества кода
make archive # Создание архива для GitHub
```

**airflow_commands.sh** - Команды Airflow:
- Инициализация и настройка
- Тестирование отдельных задач
- Управление переменными и подключениями
- Мониторинг выполнения

**demo_pipeline.py** - Демонстрационный скрипт:
- Запуск полного пайплайна без Airflow
- Проверка всех компонентов
- Создание результатов и отчетов
- Валидация окружения

## Основные файлы

| Файл | Размер | Описание |
|------|--------|----------|
| `README.md` | ~15KB | Полная документация проекта |
| `DEPLOYMENT.md` | ~8KB | Инструкции по развертыванию |
| `requirements.txt` | ~1KB | Python зависимости |
| `Makefile` | ~6KB | Команды автоматизации |
| `docker-compose.yml` | ~5KB | Инфраструктура Docker |
| `ml_pipeline_dag.py` | ~15KB | Основной DAG Airflow |
| `demo_pipeline.py` | ~5KB | Демонстрационный скрипт |

## Метрики проекта

- **Общий размер проекта**: ~150MB (включая данные и результаты)
- **Строки кода**: ~2500 строк Python кода
- **Покрытие тестами**: 80%+ всех модулей
- **Количество файлов**: ~30 файлов
- **Поддерживаемые платформы**: Linux, macOS, Windows (Docker)

## Точки входа

1. **Демонстрация**: `python demo_pipeline.py`
2. **Airflow**: `make airflow-start` → http://localhost:8080
3. **Docker**: `docker-compose up -d`
4. **Тесты**: `make test`
5. **Разработка**: `make setup`

---

**Эта структура обеспечивает полную автоматизацию, воспроизводимость и готовность к продакшн развертыванию.**
