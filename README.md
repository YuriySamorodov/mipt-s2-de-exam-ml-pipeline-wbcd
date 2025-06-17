# ML Pipeline для диагностики рака молочной железы

> **Автоматизированный ETL-пайплайн машинного обучения**
> Диагностика рака молочной железы с использованием Apache Airflow и PostgreSQL

## Содержание

### 1. Основная информация
- [О проекте](#о-проекте)
  - [Цель проекта](#цель-проекта) 
  - [Медицинское значение](#медицинское-значение)
- [Описание датасета](#описание-датасета)
  - [Wisconsin Breast Cancer Diagnostic Dataset](#wisconsin-breast-cancer-diagnostic-dataset-wbcd)
  - [Источник данных](#источник-данных)
  - [Характеристики датасета](#характеристики-датасета)
  - [Группы признаков](#группы-признаков)

### 2. Установка и запуск
- [Варианты запуска проекта](#варианты-запуска-проекта)
  - [Сравнение вариантов](#сравнение-вариантов)
  - [Выбор варианта](#выбор-варианта)
  - [Особенности каждого варианта](#особенности-каждого-варианта)
- [Локальный запуск (SQLite - Порт 8081)](#локальный-запуск-sqlite---порт-8081)
  - [Предварительные требования](#предварительные-требования)
  - [Быстрый запуск](#быстрый-запуск)
  - [Доступ к веб-интерфейсу](#доступ-к-веб-интерфейсу)
  - [Параметры конфигурации](#параметры-конфигурации)
- [Локальный запуск (PostgreSQL - Порт 8082)](#локальный-запуск-postgresql---порт-8082)
  - [Предварительные требования](#предварительные-требования-1)
  - [Быстрый запуск](#быстрый-запуск-1)
  - [Доступ к веб-интерфейсу](#доступ-к-веб-интерфейсу-1)
  - [Параметры конфигурации](#параметры-конфигурации-1)
  - [Особенности PostgreSQL-режима](#особенности-postgresql-режима)
- [Docker запуск (PostgreSQL - Порт 8083)](#docker-запуск-postgresql---порт-8083)
  - [Самый быстрый способ запуска](#самый-быстрый-способ-запуска)
  - [Доступ к веб-интерфейсу](#доступ-к-веб-интерфейсу-2)
  - [Что включает готовый образ](#что-включает-готовый-образ)
  - [Системные требования](#системные-требования)

### 3. Техническая документация
- [Сборка Docker Image](#сборка-docker-image)
  - [Автоматическая сборка](#автоматическая-сборка-рекомендуется)
  - [Ручная сборка](#ручная-сборка)
- [Структура проекта](#структура-проекта)
- [Конфигурация](#конфигурация)
- [Компоненты системы](#компоненты-системы)

### 4. Результаты и тестирование
- [Метрики и результаты](#метрики-и-результаты)
- [Тестирование](#тестирование)

### 5. Дополнительная документация
- [Альтернативная установка](#альтернативная-установка)
- [Решение проблем](#решение-проблем)
- [Подробное руководство по скачиванию Docker образа](DOCKER_IMAGE_DOWNLOAD_GUIDE.md)
- [Руководство по публикации Docker образов](DOCKER_IMAGE_PUBLISHING_GUIDE.md)
- [Справочная таблица: Скачивание Docker-образа](#справочная-таблица-скачивание-docker-образа)

---

## О проекте

Проект представляет собой **полнофункциональный автоматизированный пайплайн машинного обучения** для диагностики рака молочной железы. Система построена на основе современных технологий Data Engineering и MLOps и обеспечивает надежную, масштабируемую и воспроизводимую обработку медицинских данных.

### Цель проекта

Создание production-ready системы для **автоматической диагностики новообразований молочной железы** с использованием методов машинного обучения. Система анализирует цифровые изображения тонкоигольной аспирационной биопсии (fine needle aspirate - FNA) и классифицирует опухоли как доброкачественные или злокачественные.

### Медицинское значение

- **Ранняя диагностика**: Помощь в раннем выявлении рака молочной железы
- **Поддержка врачей**: Предоставление дополнительного инструмента для принятия решений
- **Стандартизация**: Унификация процесса анализа биопсий
- **Повышение точности**: Снижение человеческих ошибок в диагностике

## Описание датасета

### Wisconsin Breast Cancer Diagnostic Dataset (WBCD)

Проект использует знаменитый **Wisconsin Breast Cancer Diagnostic Dataset**, созданный доктором Уильямом Х. Волбергом в Университете Висконсина (https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic)

#### Источник данных
- **Авторы**: Dr. William H. Wolberg, W.N. Street, O.L. Mangasarian
- **Институт**: University of Wisconsin, Madison
- **Год**: 1995
- **Размер**: 569 образцов
- **Классы**: 2 (Malignant - злокачественная, Benign - доброкачественная)

#### Характеристики датасета

| Параметр | Значение |
|----------|----------|
| **Количество образцов** | 569 |
| **Количество признаков** | 30 |
| **Злокачественных** | 212 (37.3%) |
| **Доброкачественных** | 357 (62.7%) |
| **Пропущенные значения** | Отсутствуют |
| **Тип данных** | Численные (float) |

#### Группы признаков

Для каждого клеточного ядра вычисляются 10 основных характеристик:

1. **radius** - радиус (среднее расстояние от центра до точек периметра)
2. **texture** - текстура (стандартное отклонение значений серого)
3. **perimeter** - периметр
4. **area** - площадь
5. **smoothness** - гладкость (локальная вариация длин радиуса)
6. **compactness** - компактность (периметр² / площадь - 1.0)
7. **concavity** - вогнутость (серьезность вогнутых частей контура)
8. **concave points** - вогнутые точки (количество вогнутых частей контура)
9. **symmetry** - симметрия
10. **fractal dimension** - фрактальная размерность ("coastline approximation" - 1)

#### Статистические характеристики

Для каждой из 10 основных характеристик вычисляются:
- **mean** - среднее значение (10 признаков)
- **se** - стандартная ошибка (10 признаков)
- **worst** - наихудшее значение (среднее трех наибольших значений) (10 признаков)

**Итого: 10 × 3 = 30 признаков**

#### Примеры ключевых признаков

```
ID номер, Диагноз, radius_mean, texture_mean, perimeter_mean, area_mean, 
smoothness_mean, compactness_mean, concavity_mean, concave_points_mean, 
symmetry_mean, fractal_dimension_mean, radius_se, texture_se, perimeter_se, 
area_se, smoothness_se, compactness_se, concavity_se, concave_points_se, 
symmetry_se, fractal_dimension_se, radius_worst, texture_worst, 
perimeter_worst, area_worst, smoothness_worst, compactness_worst, 
concavity_worst, concave_points_worst, symmetry_worst, fractal_dimension_worst
```

#### Клиническая интерпретация

- **Злокачественные опухоли** обычно имеют:
- Больший размер (radius, area, perimeter)
- Неправильную форму (higher concavity, concave points)
- Неровную текстуру (higher texture values)
- Меньшую симметрию

- **Доброкачественные опухоли** характеризуются:
- Более правильной формой
- Гладкими контурами
- Меньшими размерами
- Большей симметрией

### Техническая реализация

Пайплайн автоматически обрабатывает этот датасет через следующие этапы:

1. **Загрузка данных** - автоматическое скачивание и валидация
2. **Предобработка** - нормализация, обработка выбросов
3. **Разделение** - train/test split (80/20)
4. **Обучение модели** - Logistic Regression с GridSearchCV
5. **Оценка качества** - расчет метрик и визуализация
6. **Сохранение результатов** - модель и метрики в базу данных

## Готовые Docker образы

**Готовые образы доступны на Docker Hub без необходимости сборки:**

| Компонент | Docker Hub | Команда скачивания |
|-----------|------------|-------------------|
| **Airflow + ML Pipeline** | [yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest](https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline/tags?name=airflow) | `docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest` |
| **PostgreSQL** | [yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest](https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline/tags?name=postgres) | `docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest` |

## Быстрый старт

Допускается **три варианта запуска** в зависимости от потребностей:

### Вариант 1: Локальная разработка (SQLite + SequentialExecutor)
**Без Docker** - Идеально для разработки и тестирования

```bash
# 1. Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# 2. Запуск локально
./start_airflow_sqlite.sh
```

**Особенности:**
- **База данных**: SQLite (файл)
- **Исполнитель**: SequentialExecutor (задачи выполняются последовательно)
- **Запуск**: Быстрый старт без внешних зависимостей
- **Использование**: Разработка, отладка, тестирование

### Вариант 2: Готовый образ (PostgreSQL + LocalExecutor)
**С Docker** - Самый быстрый старт, готовый образ

```bash
# 1. Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# 2. Запуск (образ уже собран)
docker-compose up -d
```

**Особенности:**
- **Образ**: Готовый Docker образ `yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest`
- **База данных**: PostgreSQL (в контейнере)
- **Исполнитель**: LocalExecutor (параллельное выполнение задач)
- **Скорость**: Мгновенный запуск без сборки
- **Использование**: Быстрое тестирование, демо, обучение

### Вариант 3: Локальная сборка (PostgreSQL + LocalExecutor)
**С Docker** - Полный контроль над сборкой

```bash
# 1. Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# 2. Сборка образа локально
./build_docker_image.sh

# 3. Запуск в Docker
docker-compose up -d
```

**Особенности:**
- **Сборка**: Локальная сборка из исходников
- **База данных**: PostgreSQL (в контейнере)
- **Исполнитель**: LocalExecutor (параллельное выполнение задач)
- **Изоляция**: Полная изоляция в контейнерах
- **Использование**: Production, CI/CD, кастомизация

### Доступ к системе (оба варианта)
- **Airflow WebUI**: http://localhost:8080
- **Логин**: `admin`
- **Пароль**: `admin`

### Проверка работы
```bash
# Статус системы (для Docker)
docker ps

# Статус системы (для локального)
ps aux | grep airflow

# Запуск ML пайплайна
curl -X POST "http://localhost:8080/api/v1/dags/breast_cancer_ml_pipeline/dagRuns" \
-H "Content-Type: application/json" \
-d '{"dag_run_id": "manual_test_run"}' \
--user admin:admin
```

Полностью автоматизированный пайплайн машинного обучения для **бинарной классификации** новообразований молочной железы на основе датасета Wisconsin Breast Cancer Diagnostic.

### Ключевые особенности

| Особенность | Описание |
|-------------|----------|
| **Ready-to-use** | Готовые образы на Docker Hub - не требуется сборка |
| **Docker-Ready** | Запуск одной командой, без настройки окружения |
| **Автоматизация** | Полный ETL-цикл от данных до результатов |
| **PostgreSQL Backend** | Production-ready хранение метаданных |
| **Apache Airflow** | Оркестрация с веб-интерфейсом и мониторингом |
| **ML Pipeline** | Логистическая регрессия с подбором гиперпараметров |
| **Оптимизированный** | Единый Docker-образ, экономия ~8GB места |

### Задача машинного обучения

- **Тип**: Бинарная классификация
- **Цель**: Диагноз (Злокачественная/Доброкачественная)
- **Данные**: 30 численных характеристик клеточных ядер
- **Алгоритм**: Логистическая регрессия + GridSearchCV
- **Метрики**: Accuracy, Precision, Recall, F1-Score, ROC-AUC

## Архитектура системы

### Docker-окружение (рекомендуемое)

```mermaid
graph TB
subgraph "Docker Compose"
A[yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest<br/>Готовый образ Airflow + ML Pipeline]
B[postgres:13<br/>600MB - БД]
end

subgraph "Airflow Components"
A --> C[Webserver :8080]
A --> D[Scheduler]
A --> E[Init Container]
end

subgraph "Data Flow"
F[wdbc.data.csv] --> G[ETL Pipeline]
G --> H[ML Model]
H --> I[Results & Metrics]
end

C --> G
D --> G
B --> C
B --> D

style A fill:#e3f2fd
style B fill:#f1f8e9
style I fill:#fff3e0
```

## Варианты запуска проекта

Проект поддерживает **три варианта запуска** с различными конфигурациями Executor и портами веб-сервера:

### Сравнение вариантов

| Вариант | База данных | Executor | Порт | Команда запуска |
|---------|-------------|----------|------|----------------|
| **SQLite** | SQLite | SequentialExecutor | 8081 | `./start-sqlite.sh` |
| **PostgreSQL** | PostgreSQL | LocalExecutor* | 8082 | `./start-postgres.sh` |
| **Docker** | PostgreSQL | LocalExecutor | 8083 | `docker-compose up -d` |

> **Примечание**: В варианте PostgreSQL multiprocessing был заменен на ThreadPoolExecutor для улучшенной совместимости с macOS.

### Выбор варианта

- **SQLite (8081)** - для быстрого старта и разработки, не требует внешних зависимостей
- **PostgreSQL (8082)** - для полнофункционального тестирования с параллельным выполнением
- **Docker (8083)** - для production-окружения с полной изоляцией

### Особенности каждого варианта

#### 1. SQLite (Порт 8081)
- **Executor**: SequentialExecutor (одна задача за раз)
- **База данных**: Локальный SQLite файл
- **Преимущества**: Быстрый старт, нет внешних зависимостей
- **Недостатки**: Нет параллельного выполнения

#### 2. PostgreSQL (Порт 8082)
- **Executor**: LocalExecutor с ThreadPoolExecutor
- **База данных**: Локальный PostgreSQL
- **Преимущества**: Параллельное выполнение, совместимость с macOS
- **Недостатки**: Требует установки PostgreSQL

#### 3. Docker (Порт 8083)
- **Executor**: LocalExecutor (стандартный)
- **База данных**: PostgreSQL в контейнере
- **Преимущества**: Полная изоляция, готово к production
- **Недостатки**: Требует Docker

## Локальный запуск (SQLite - Порт 8081)

### Предварительные требования
- **Python**: Версия 3.8+
- **Pip**: Для установки зависимостей
- **Свободное место**: ~500MB для зависимостей

### Быстрый запуск
```bash
# Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# Автоматический запуск (создаст venv, установит зависимости)
./start-sqlite.sh
```

### Доступ к веб-интерфейсу
- **URL**: http://localhost:8081
- **Логин**: admin
- **Пароль**: admin

### Параметры конфигурации
```bash
export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:///airflow_home/airflow.db"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8081
```

### Остановка
```bash
./stop_airflow_sqlite.sh
```

### Особенности SQLite-режима
| Особенность | Значение |
|-------------|----------|
| **База данных** | SQLite файл (легковесная) |
| **Исполнитель** | SequentialExecutor (безопасно) |
| **Запуск** | Без внешних зависимостей |
| **Цель** | Разработка, отладка, обучение |
| **Производительность** | Одна задача за раз |
| **Изоляция** | Без контейнеров |

---

## Локальный запуск (PostgreSQL - Порт 8082)

### Предварительные требования
- **Python**: Версия 3.8+
- **PostgreSQL**: Версия 12+
- **Pip**: Для установки зависимостей
- **Свободное место**: ~1GB для зависимостей и БД

### Быстрый запуск
```bash
# Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# Автоматический запуск с PostgreSQL
./start-postgres.sh
```

### Доступ к веб-интерфейсу
- **URL**: http://localhost:8082
- **Логин**: admin  
- **Пароль**: admin

### Параметры конфигурации
```bash
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost/airflow"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8082
```

### Особенности PostgreSQL-режима
| Особенность | Значение |
|-------------|----------|
| **База данных** | PostgreSQL (локальная) |
| **Исполнитель** | LocalExecutor с ThreadPoolExecutor |
| **Совместимость** | Оптимизировано для macOS |
| **Производительность** | Параллельное выполнение задач |
| **Цель** | Тестирование, разработка с параллелизмом |

> **Важно**: В этом варианте multiprocessing был заменен на ThreadPoolExecutor для решения проблем совместимости с macOS, особенно при работе с fork() системными вызовами.

### Остановка
```bash
./stop-postgres.sh
```

### Пример работы с PostgreSQL
![Главное окно Airflow](https://github.com/YuriySamorodov/mipt-s2-de-exam-ml-pipeline-wbcd/blob/main/screenshots/setup/Airflow%20-%20two%20webservers%20together.png)
*Подключение к базе данных PostgreSQL с загруженными данными*

---

## Docker запуск (PostgreSQL - Порт 8083)

### Самый быстрый способ запуска
Для экономии времени можно использовать готовые образы `yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest`.

```bash
# Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# Мгновенный запуск (образ уже готов)
docker-compose up -d
```

### Доступ к веб-интерфейсу
- **URL**: http://localhost:8083
- **Логин**: admin
- **Пароль**: admin

### Что включает готовый образ
- **Apache Airflow 2.8.1** с оптимизированными настройками
- **Python 3.10** с установленными ML библиотеками
- **ETL модули** предустановлены и настроены
- **DAG файлы** готовы к запуску
- **Конфигурация** оптимизирована для production

### Системные требования
| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| **RAM** | 4GB | 8GB+ |
| **Диск** | 6GB свободного места | 10GB+ |
| **Интернет** | Для скачивания (3GB) | Стабильное соединение |
| **Docker** | v20.10+ | Latest stable |
| **Docker Compose** | v2.0+ | Latest stable |

### Информация об образе
```bash
# Размер и слои образа
docker history ml-pipeline-airflow:latest

# Детальная информация
docker inspect ml-pipeline-airflow:latest | jq '.Config'

# Переменные окружения
docker run --rm ml-pipeline-airflow:latest env | grep AIRFLOW
```

### Преимущества готового образа
| Преимущество | Описание |
|--------------|----------|
| **Скорость** | Запуск за 2-3 минуты вместо 10-15 минут сборки |
| **Стабильность** | Протестированный и оптимизированный образ |
| **Размер** | Единый образ 2.84GB (экономия ~5.68GB) |
| **Готовность** | Все зависимости предустановлены |

### Состав готового образа
```dockerfile
# Базовый образ: apache/airflow:2.8.1-python3.10
# Размер: 2.84GB
# Включает:
Python ML библиотеки (pandas, scikit-learn, joblib)
ETL модули (data_loader, preprocessor, trainer, metrics)
DAG файлы (breast_cancer_ml_pipeline)
Конфигурационные файлы
Тестовые данные (wdbc.data.csv)
```

### Скачивание готового образа

#### Быстрые команды
```bash
# Способ 1: Автоматически при запуске (рекомендуется)
docker-compose up -d # Образ скачается автоматически

# Способ 2: Принудительное обновление
docker-compose pull && docker-compose up -d

# Способ 3: Ручное скачивание
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest
```

#### Автоматическое скачивание (рекомендуется)
При запуске `docker-compose up -d` образ автоматически скачается из реестра:

```bash
# Docker автоматически скачает образ при первом запуске
docker-compose up -d

# Или принудительно обновить образ
docker-compose pull
```

#### Ручное скачивание образа
```bash
# Скачивание готового образа
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest

# Доступные теги
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-v1.0.0
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-v1.0.0
```

#### Источники образа

**Основные реестры Docker:**

| Компонент | Образ | Docker Hub URL | Команда |
|-----------|-------|----------------|---------|
| **Airflow + ML** | `airflow-latest` | [yuriysamorodov/mipt-s2-de-ml-pipeline](https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline) | `docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest` |
| **PostgreSQL** | `postgres-latest` | [yuriysamorodov/mipt-s2-de-ml-pipeline](https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline) | `docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:postgres-latest` |

> **Актуальные ссылки**:
> - Airflow: https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline/tags?name=airflow
> - PostgreSQL: https://hub.docker.com/r/yuriysamorodov/mipt-s2-de-ml-pipeline/tags?name=postgres

#### Альтернативные способы получения образа

**1. Из локальной сборки:**
```bash
# Если образ собран локально
./build_docker_image.sh
# Образ ml-pipeline-airflow:latest будет доступен
```

**2. Экспорт/импорт образа:**
```bash
# Экспорт образа в файл
docker save yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest > ml-pipeline-airflow.tar

# Импорт образа из файла
docker load < ml-pipeline-airflow.tar
```

**3. Из CI/CD artifacts:**
```bash
# Скачивание из CI/CD системы (пример)
curl -O https://artifacts.company.com/mipt-s2-de-ml-pipeline-latest.tar
docker load < mipt-s2-de-ml-pipeline-latest.tar
```

**4. Прямое скачивание архива:**
```bash
# Скачивание готового образа как файл (пока не реализовано)
wget https://releases.company.com/mipt-s2-de-ml-pipeline-v1.0.0.tar.gz
tar -xzf ml-pipeline-airflow-v2.0.0.tar.gz
docker load < ml-pipeline-airflow.tar
```

**5. Локальные файлы образов:**
```bash
# Если образы экспортированы в папку docker-images/
gunzip -c docker-images/ml-pipeline-airflow-latest.tar.gz | docker load

# Или импорт без сжатия (быстрее)
docker load < docker-images/ml-pipeline-airflow-latest.tar
```

**5. Альтернативные зеркала:**
```bash
# Китайские зеркала (для пользователей в Азии)
docker pull registry.cn-hangzhou.aliyuncs.com/ml-pipeline/airflow:latest

# Европейские зеркала
docker pull eu.gcr.io/ml-pipeline/airflow:latest

# Российские зеркала
docker pull cr.yandex/ml-pipeline/airflow:latest
```

#### Аутентификация (для приватных реестров)

```bash
# Вход в Docker Hub
docker login

# Вход в GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Вход в приватный реестр
docker login registry.company.com
```

#### Проверка скачивания
```bash
# Проверка успешного скачивания
docker images ml-pipeline-airflow

# Должен показать что-то вроде:
# REPOSITORY TAG IMAGE ID CREATED SIZE
# ml-pipeline-airflow latest 667511c0b76d 2 hours ago 2.84GB

# Проверка целостности образа
docker inspect ml-pipeline-airflow:latest | grep -A 10 "RepoDigests"

# Быстрая проверка работоспособности
docker run --rm ml-pipeline-airflow:latest airflow version
```

#### Верификация образа
```bash
# Проверка подписи образа (если доступна)
docker trust inspect ml-pipeline-airflow:latest

# Сканирование на уязвимости (опционально)
docker scout quickview ml-pipeline-airflow:latest

# Проверка содержимого образа
docker run --rm ml-pipeline-airflow:latest ls -la /opt/airflow/dags/
```

#### Troubleshooting скачивания

**Проблема: Образ не найден**
```bash
# 1. Проверка доступных тегов
docker search ml-pipeline-airflow

# 2. Использование альтернативного реестра
docker pull ghcr.io/ml-pipeline/ml-pipeline-airflow:latest

# 3. Проверка конкретного реестра
curl -s https://registry.hub.docker.com/v2/repositories/ml-pipeline-airflow/tags/
```

**Проблема: Медленное скачивание**
```bash
# 1. Использование CDN зеркала
docker pull --disable-content-trust registry.cn-hangzhou.aliyuncs.com/ml-pipeline/airflow:latest

# 2. Параллельное скачивание слоев
docker pull --parallel ml-pipeline-airflow:latest

# 3. Проверка сетевых настроек
docker system info | grep -i proxy
```

**Проблема: Ошибка аутентификации**
```bash
# 1. Проверка токена
docker login --username=your-username

# 2. Для GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 3. Очистка кеша аутентификации
docker logout
docker system prune -a
```

**Проблема: Недостаточно места**
```bash
# 1. Очистка старых образов
docker image prune -a

# 2. Проверка свободного места
df -h
docker system df

# 3. Альтернативное расположение
export DOCKER_TMPDIR=/path/to/large/disk
docker pull yuriysamorodov/mipt-s2-de-ml-pipeline:airflow-latest
```

**Проблема: Корпоративная сеть/прокси**
```bash
# 1. Настройка прокси для Docker
# Добавить в ~/.docker/config.json:
{
"proxies": {
"default": {
"httpProxy": "http://proxy.company.com:8080",
"httpsProxy": "http://proxy.company.com:8080"
}
}
}

# 2. Обход прокси для локальных адресов
export NO_PROXY=localhost,127.0.0.1,docker-registry.company.com
```

### Проверка образа
```bash
# Проверка наличия образа
docker images ml-pipeline-airflow

# Информация об образе
docker inspect ml-pipeline-airflow:latest

# Проверка версий внутри образа
docker run --rm ml-pipeline-airflow:latest python --version
docker run --rm ml-pipeline-airflow:latest airflow version
```

### Особенности готового образа
| Особенность | Значение |
|-------------|----------|
| **База данных** | PostgreSQL (в контейнере) |
| **Исполнитель** | LocalExecutor (параллельно) |
| **Запуск** | 2-3 минуты до готовности |
| **Цель** | Быстрое тестирование, демо |
| **Производительность** | Высокая (параллельные задачи) |
| **Изоляция** | Полная (Docker контейнеры) |

---

## Docker Setup (PostgreSQL)

### Предварительные требования
- **Docker Desktop**: Версия 20.10+
- **Docker Compose**: Версия 2.0+
- **Свободное место**: ~4GB для образов

### Автоматический запуск
```bash
# Клонирование проекта
git clone <repository-url>
cd ml-pipeline-project

# Запуск системы
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### Доступ к веб-интерфейсу
- **URL**: http://localhost:8083
- **Логин**: admin
- **Пароль**: admin

### Параметры конфигурации
```bash
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@postgres/airflow"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8083
```

### Особенности Docker-режима
| Особенность | Значение |
|-------------|----------|
| **База данных** | PostgreSQL (в контейнере) |
| **Исполнитель** | LocalExecutor (стандартный) |
| **Изоляция** | Полная контейнеризация |
| **Производительность** | Высокая (параллельные задачи) |
| **Цель** | Production, полное тестирование |
| **Масштабируемость** | Готов к кластеризации |

### Ручные команды
```bash
# Проверка образов
docker images | grep ml-pipeline

# Просмотр логов
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler

# Остановка системы
docker-compose down

# Полная очистка (с данными)
docker-compose down -v
```

### Пример Docker
![Docker Web](https://github.com/YuriySamorodov/mipt-s2-de-exam-ml-pipeline-wbcd/blob/main/screenshots/setup/docker%20hub%20webui%202.png)
*Образы Docker в Docker Hub*

![Docker Desktop](https://github.com/YuriySamorodov/mipt-s2-de-exam-ml-pipeline-wbcd/blob/main/screenshots/setup/Docker%20Desktop.png)

![Docker Deploy](screenshots/setup/docker%20deploy.png)
*Пример развертывания ML Pipeline в Docker с использованием docker-compose*

## Сборка Docker Image

### Автоматическая сборка (рекомендуется)
```bash
# Автоматическая сборка образа с проверками
./build_docker_image.sh
```

**Что делает скрипт:**
1. Проверяет наличие всех необходимых файлов
2. Собирает образ используя `Dockerfile.local`
3. Показывает информацию о размере образа
4. Готовит образ для использования в `docker-compose`

### Ручная сборка
```bash
# Сборка с использованием Dockerfile.local
docker build -t ml-pipeline-airflow:latest -f Dockerfile.local .

# Проверка созданного образа
docker images ml-pipeline-airflow

# Дополнительная оптимизация (опционально)
./optimize_docker_images.sh
```

### Структура Dockerfile.local
```dockerfile
FROM apache/airflow:2.8.1-python3.10
USER root

# Системные зависимости для ML
RUN apt-get update && apt-get install -y \
build-essential \
libpq-dev \
gcc g++ curl \
&& rm -rf /var/lib/apt/lists/*

USER airflow

# Python зависимости проекта
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Копирование файлов проекта
COPY --chown=airflow:root ./dags /opt/airflow/dags
COPY --chown=airflow:root ./etl /opt/airflow/etl
COPY --chown=airflow:root ./config /opt/airflow/config
COPY --chown=airflow:root ./data /opt/airflow/data

# Создание директорий для результатов
RUN mkdir -p /opt/airflow/results/{models,metrics,plots} \
/opt/airflow/logs

# Health check для контейнера
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=5 \
CMD airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}" \
|| curl --fail http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["webserver"]
```

### Требуемые файлы для сборки
Убедитесь, что следующие файлы присутствуют:
- `Dockerfile.local` - основной Dockerfile
- `requirements.txt` - Python зависимости
- `dags/` - директория с DAG файлами
- `etl/` - ETL модули
- `config/` - конфигурационные файлы
- `data/` - исходные данные

### Сравнение методов сборки

| Метод | Dockerfile | Цель | Особенности |
|-------|------------|------|-------------|
| **Автоматический** | `Dockerfile.local` | Локальная разработка | Скрипт с проверками |
| **Production** | `Dockerfile.airflow` | Готовый образ | Оптимизированный размер |
| **Оптимизированный** | + скрипт | Экономия места | Удаление дубликатов |

## Запуск проекта

### 1. Простой запуск
```bash
# Запуск в фоновом режиме
docker-compose up -d

# Ожидание готовности сервисов (~2-3 минуты)
docker-compose ps
```

### 2. Доступ к интерфейсам
- **Airflow Web UI**: http://localhost:8083
- Логин: `admin`
- Пароль: `admin`
- **PostgreSQL**: localhost:5432
- База: `airflow`
- Пользователь: `airflow`
- Пароль: `airflow`

### 3. Проверка DAG
```bash
# Список DAG
curl -X GET "http://localhost:8083/api/v1/dags" --user admin:admin

# Запуск ML пайплайна
curl -X POST "http://localhost:8083/api/v1/dags/breast_cancer_ml_pipeline/dagRuns" \
-H "Content-Type: application/json" \
-d '{"dag_run_id": "manual_run_$(date +%s)"}' \
--user admin:admin
```

### 4. Мониторинг выполнения
- **Веб-интерфейс**: График состояния задач
- **Логи**: `docker-compose logs -f airflow-scheduler`
- **Результаты**: Директория `./results/`

## Структура проекта

```
ml-pipeline-project/
├── README.md                          # Основная документация
├── requirements.txt                   # Основные зависимости Python
├── pytest.ini                        # Конфигурация тестирования
├── Makefile                          # Автоматизация задач
├── .gitignore                        # Git ignore файл
├── .env.example                      # Пример переменных окружения
│
├── data/                             # Данные проекта
│   └── wdbc.data.csv                # Датасет Wisconsin Breast Cancer
│
├── src/                              # Исходный код приложения
│   ├── __init__.py
│   ├── etl/                         # ETL модули для обработки данных
│   │   ├── __init__.py
│   │   ├── data_loader.py           # Загрузка и валидация данных
│   │   ├── data_preprocessor.py     # Предобработка и очистка данных
│   │   ├── data_quality_controller.py # Контроль качества данных  
│   │   ├── metrics_calculator.py    # Расчет метрик модели
│   │   ├── model_trainer.py         # Обучение ML моделей
│   │   └── storage_manager.py       # Управление сохранением результатов
│   ├── pipelines/                   # Pipeline скрипты
│   │   ├── demo_pipeline.py         # Демонстрационный пайплайн
│   │   ├── run_pipeline.py          # Основной запуск пайплайна
│   │   └── run_full_pipeline_sqlite.py # Полный пайплайн для SQLite
│   └── utils/                       # Утилиты и вспомогательные функции
│       ├── clean_brackets.py        # Очистка от лишних символов
│       ├── fix_formatting.py        # Форматирование кода
│       └── remove_emojis.py         # Удаление эмодзи из файлов
│
├── dags/                            # Airflow DAG файлы
│   ├── ml_pipeline_dag.py           # Основной ML пайплайн DAG
│   ├── simple_test_dag.py           # Простой тестовый DAG
│   └── simple_test_dag_working.py   # Рабочая версия тестового DAG
│
├── tests/                           # Тестирование
│   ├── conftest.py                  # Конфигурация pytest
│   ├── test_data_loader.py          # Тесты загрузчика данных
│   ├── test_data_preprocessor.py    # Тесты предобработчика
│   ├── test_metrics_calculator.py   # Тесты расчета метрик
│   ├── test_model_trainer.py        # Тесты обучения модели
│   ├── test_storage_manager.py      # Тесты менеджера хранения
│   └── integration/                 # Интеграционные тесты
│       └── test_integration.py      # Комплексное тестирование
│
├── scripts/                         # Скрипты управления и настройки
│   ├── activate_venv.sh             # Активация виртуального окружения
│   ├── airflow/                     # Airflow управление
│   │   ├── start_airflow_*.sh       # Скрипты запуска Airflow
│   │   └── stop_airflow_*.sh        # Скрипты остановки Airflow
│   ├── database/                    # Управление базами данных
│   │   ├── fix_airflow_db*.py       # Исправление БД Airflow
│   │   └── optimize_postgresql.sh   # Оптимизация PostgreSQL
│   ├── docker/                      # Docker операции
│   │   ├── build_docker_*.sh        # Сборка Docker образов
│   │   └── publish_docker_image.sh  # Публикация образов
│   ├── setup/                       # Настройка окружения
│   │   └── setup_single_repo.sh     # Настройка единого репозитория
│   └── testing/                     # Тестовые скрипты
│       ├── test_*.py                # Различные тесты
│       ├── run_tests.py             # Запуск всех тестов
│       └── integration_test.sh      # Интеграционное тестирование
│
├── docker/                          # Docker конфигурации
│   ├── Dockerfile                   # Основной Dockerfile
│   ├── Dockerfile.local             # Локальная сборка
│   ├── Dockerfile.postgres          # PostgreSQL версия
│   ├── Dockerfile.airflow           # Airflow версия
│   ├── Dockerfile.unified           # Объединенная версия
│   ├── docker-compose.yml           # Основная композиция
│   ├── docker-compose-optimized.yml # Оптимизированная версия
│   ├── docker-compose-original.yml  # Оригинальная версия
│   ├── gunicorn.conf.py             # Конфигурация Gunicorn
│   ├── configs/                     # Конфигурации для контейнеров
│   │   └── init-postgres.sh         # Инициализация PostgreSQL
│   └── scripts/                     # Скрипты для контейнеров
│
├── config/                          # Конфигурационные файлы
│   ├── config.yaml                  # Основная конфигурация
│   ├── config_utils.py              # Утилиты конфигурации
│   ├── airflow_optimized.cfg.patch  # Патч для оптимизации Airflow
│   └── requirements/                # Файлы зависимостей
│       ├── requirements.txt         # Основные зависимости
│       ├── requirements-airflow.txt # Airflow зависимости
│       ├── requirements.minimal.txt # Минимальные зависимости
│       ├── requirements.simple.txt  # Простые зависимости
│       └── requirements_final.txt   # Финальные зависимости
│
├── docs/                            # Документация проекта
│   ├── AIRFLOW_VARIANTS.md          # Варианты развертывания Airflow
│   ├── guides/                      # Руководства пользователя
│   │   ├── QUICK_START.md           # Быстрый старт
│   │   ├── DEPLOYMENT.md            # Руководство по развертыванию
│   │   ├── DOCKER_IMAGE_*.md        # Руководства по Docker
│   │   └── LAUNCH_OPTIONS_GUIDE.md  # Опции запуска
│   ├── development/                 # Документация для разработчиков
│   │   └── ALTERNATIVE_SOLUTIONS.md # Альтернативные решения
│   └── reports/                     # Отчеты и результаты
│       ├── RESULTS_INDEX.md         # Индекс результатов
│       └── RESULTS_INTERPRETATION.md # Интерпретация результатов
│
├── screenshots/                     # Скриншоты и изображения
│   ├── README.md                    # Описание скриншотов
│   ├── QUICK_COMMANDS.md            # Быстрые команды
│   ├── airflow/                     # Скриншоты Airflow UI
│   ├── database/                    # Скриншоты БД
│   ├── monitoring/                  # Скриншоты мониторинга
│   ├── results/                     # Скриншоты результатов
│   └── setup/                       # Скриншоты настройки
│
├── results/                         # Результаты выполнения
│   └── (генерируются автоматически)
│
├── logs/                           # Логи системы
│   └── (генерируются автоматически)
│
├── plugins/                        # Airflow плагины
│   └── (пользовательские плагины)
│
├── airflow/                        # Airflow home директория
│   ├── airflow.cfg                 # Конфигурация Airflow
│   ├── airflow.db                  # SQLite база данных
│   └── logs/                       # Логи Airflow
│
├── venv/                           # Виртуальное окружение Python
│   └── (создается автоматически)
│
└── Скрипты запуска (в корне):      # Основные команды управления
    ├── start-sqlite.sh             # SQLite запуск (порт 8081)
    ├── start-postgres.sh           # PostgreSQL запуск (порт 8082)
    ├── start-docker.sh             # Docker запуск (порт 8083)
    ├── activate_venv.sh            # Активация окружения
    ├── test_sqlite.sh              # Тестирование SQLite
    ├── alias_start_airflow_*.sh    # Алиасы для запуска
    ├── wrapper_start_airflow_*.sh  # Обертки для запуска
    ├── set_absolute_paths_env.py   # Настройка путей
    ├── fix_*.py                    # Скрипты исправлений
    └── *_cleanup.sh               # Скрипты очистки
```

### Ключевые компоненты

#### 🔧 Исходный код (`src/`)
- **ETL модули**: Полный цикл обработки данных от загрузки до сохранения
- **Pipelines**: Готовые пайплайны для различных сценариев
- **Utils**: Вспомогательные утилиты и инструменты

#### 📊 DAGs (`dags/`) 
- **ML Pipeline DAG**: Основной пайплайн машинного обучения
- **Test DAGs**: Тестовые пайплайны для проверки функциональности

#### 🐳 Docker (`docker/`)
- **Множественные Dockerfile**: Для различных сценариев развертывания
- **Docker Compose**: Оркестрация многоконтейнерных приложений
- **Конфигурации**: Настройки для production окружения

#### ⚙️ Конфигурация (`config/`)
- **Файлы зависимостей**: Различные наборы requirements для разных целей
- **Конфигурационные файлы**: YAML и Python конфигурации
- **Патчи оптимизации**: Улучшения производительности

#### 🧪 Тестирование (`tests/`)
- **Unit тесты**: Тестирование отдельных компонентов
- **Integration тесты**: Комплексное тестирование системы
- **Конфигурация pytest**: Настройки тестового окружения
│ │ ├── DEPLOYMENT.md # Развертывание
│ │ └── DOCKER_*.md # Docker руководства
│ ├── reports/ # Технические отчеты
│ │ ├── FINAL_*.md # Финальные отчеты
│ │ ├── PROJECT_*.md # Отчеты по проекту
│ │ └── OPTIMIZATION_*.md # Отчеты по оптимизации
│ └── development/ # Документация разработки
│ ├── ALTERNATIVE_SOLUTIONS.md # Альтернативные решения
│ └── TESTING_STRATEGY.md # Стратегия тестирования
│
├── tests/ # Тесты
│ ├── conftest.py # Конфигурация pytest
│ ├── test_*.py # Unit тесты
│ └── integration/ # Интеграционные тесты
│ └── test_integration.py # Интеграционные тесты
│
├── data/ # Данные
│ └── (файлы данных)
│
├── results/ # Результаты выполнения
│ └── (результаты работы ML)
│
├── logs/ # Логи
│ └── (логи системы)
│
├── airflow/ # Airflow домашняя директория
│ └── (файлы Airflow)
│
└── screenshots/ # Скриншоты для документации
└── (скриншоты интерфейсов)
```

### Пайплайн выполнения

```mermaid
graph TB
A[ load_data] --> B[ validate_data]
B --> C[ preprocess_data]
C --> D[ split_data]
D --> E[ normalize_features]
E --> F[ train_model]
F --> G[ tune_hyperparameters]
G --> H[ evaluate_model]
H --> I[ calculate_metrics]
I --> J[ create_visualizations]
J --> K[ save_results]
K --> L[ upload_to_cloud]

style A fill:#e3f2fd
style F fill:#f3e5f5
style I fill:#e8f5e8
style L fill:#fff3e0
```

### Задачи (Tasks) в DAG

| Задача | Описание | Время выполнения |
|---------|----------|------------------|
| `load_data` | Загрузка CSV файла, валидация схемы | ~5 сек |
| `validate_data` | Проверка качества данных, статистика | ~3 сек |
| `preprocess_data` | Очистка, кодирование целевой переменной | ~2 сек |
| `split_data` | Разделение train/test (80/20) | ~1 сек |
| `normalize_features` | StandardScaler нормализация | ~1 сек |
| `train_model` | Логистическая регрессия | ~2 сек |
| `tune_hyperparameters` | GridSearchCV (C, penalty) | ~15 сек |
| `evaluate_model` | Предсказание на test выборке | ~1 сек |
| `calculate_metrics` | Accuracy, Precision, Recall, F1, ROC-AUC | ~2 сек |
| `create_visualizations` | Confusion Matrix, ROC Curve | ~5 сек |
| `save_results` | Сохранение модели и метрик | ~3 сек |
| `upload_to_cloud` | Загрузка в облачное хранилище | ~10 сек |

**Общее время**: ~50 секунд
## Конфигурация

### Переменные окружения (.env)
```bash
# Airflow
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=.
_PIP_ADDITIONAL_REQUIREMENTS=pandas scikit-learn joblib pyyaml python-dotenv

# PostgreSQL
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Cloud Storage (опционально)
CLOUD_BUCKET_NAME=your-bucket-name
CLOUD_ACCESS_KEY=your-access-key
CLOUD_SECRET_KEY=your-secret-key
```

### config.yaml структура
```yaml
# Конфигурация ML Pipeline
data:
input_file: "data/wdbc.data.csv"
target_column: "diagnosis"
test_size: 0.2
random_state: 42

model:
algorithm: "LogisticRegression"
hyperparameters:
C: [0.01, 0.1, 1.0, 10.0, 100.0]
penalty: ['l1', 'l2']
solver: ['liblinear']
cross_validation_folds: 5

output:
models_dir: "results/models"
metrics_dir: "results/metrics"
plots_dir: "results"

cloud:
enabled: false
provider: "s3" # или "gcs", "azure"
bucket_name: "${CLOUD_BUCKET_NAME}"
```

### Docker Compose детали
```yaml
version: '3.8'

services:
# Единый Airflow образ для всех компонентов
airflow-webserver:
image: ml-pipeline-airflow:latest
ports:
- "8080:8080"
healthcheck:
test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
interval: 30s
timeout: 10s
retries: 5

airflow-scheduler:
image: ml-pipeline-airflow:latest
command: scheduler
healthcheck:
test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
interval: 30s
timeout: 10s
retries: 5

postgres:
image: postgres:13
environment:
POSTGRES_USER: airflow
POSTGRES_PASSWORD: airflow
POSTGRES_DB: airflow
volumes:
- postgres_db_volume:/var/lib/postgresql/data
healthcheck:
test: ["CMD", "pg_isready", "-U", "airflow"]
interval: 10s
timeout: 5s
retries: 5
```

## Быстрый старт

### **РЕКОМЕНДУЕМЫЙ СПОСОБ: Docker (Production-Ready)**

**Требования:** Docker Desktop

1. **Клонирование и запуск**
```bash
git clone <repository-url>
cd ml-pipeline-project
./start_airflow_docker.sh
```

2. **Проверка работы**
- Web-интерфейс: http://localhost:8080 (admin/admin)
- Статус контейнеров: `docker ps`
- Логи: `docker-compose logs -f`

3. **Тестирование DAG**
```bash
# Запуск в браузере или через curl
curl http://localhost:8080/dags/breast_cancer_ml_pipeline/trigger
```

**Остановка:**
```bash
docker-compose down
```

---

### **Альтернативный способ: Нативная установка**

#### Предварительные требования
- Python 3.8+
- PostgreSQL 13+
- Apache Airflow 2.8+

#### Установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd ml-pipeline-project
```

2. **Настройка PostgreSQL**
```bash
# Создание базы данных и пользователя
createdb airflow_db
createuser -s airflow_user
psql -c "ALTER USER airflow_user PASSWORD 'airflow_pass';"
```

3. **Настройка окружения**
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Инициализация Airflow
source ./airflow_postgresql_env.sh
airflow db init
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

#### Запуск Airflow

**Рекомендуемый способ:**
```bash
# Автоматический запуск всех сервисов
./start_airflow.sh
```

**Режим разработки (debug):**
```bash
./start_airflow.sh --dev
```

#### Проверка работы

После запуска проверьте:
- Web-интерфейс: http://localhost:8080 (admin/admin)
- Статус процессов: `ps aux | grep -E "(airflow|gunicorn)"`
- Логи: `logs/scheduler.log`, `logs/webserver.log`

#### Остановка сервисов

```bash
pkill -f airflow && pkill -f gunicorn
```

## Конфигурация

Основная конфигурация находится в файле `config/config.yaml`:

```yaml
data:
source_file: \"data/wdbc.data.csv\"
test_size: 0.2
random_state: 42

model:
type: \"LogisticRegression\"
parameters:
random_state: 42
max_iter: 1000
solver: \"liblinear\"

storage:
local:
results_path: \"results/\"
gcs:
bucket_name: \"ml-pipeline-results\"
credentials_path: \"config/gcs-credentials.json\"

airflow:
dag_id: \"breast_cancer_ml_pipeline\"
schedule_interval: null
retries: 2
timeout_minutes: 30
```

### Переменные Airflow

Настройте следующие переменные в Airflow UI:

| Переменная | Тип | Значение по умолчанию | Описание |
|------------|-----|----------------------|----------|
| `use_hyperparameter_tuning` | boolean | true | Использовать подбор гиперпараметров |
| `upload_to_cloud` | boolean | false | Загружать результаты в облако |
| `cleanup_max_age_days` | integer | 30 | Максимальный возраст файлов для очистки |

### Мониторинг

- Все задачи логируются с детальной информацией
- Результаты передаются между задачами через XCom
- Email уведомления при ошибках
- Веб-интерфейс для мониторинга выполнения

### Запуск DAG

```bash
# Через Airflow CLI
airflow dags trigger breast_cancer_ml_pipeline

# Тестирование отдельной задачи
airflow tasks test breast_cancer_ml_pipeline load_and_validate_data 2024-01-01
```

## Тестирование

Проект включает комплексную стратегию тестирования, обеспечивающую высокое качество и надежность кода.

### Структура тестов

#### Unit тесты (Модульные тесты)
- **`test_data_loader.py`** - тестирование загрузки и валидации данных
- **`test_data_preprocessor.py`** - тестирование предобработки данных
- **`test_model_trainer.py`** - тестирование обучения моделей
- **`test_metrics_calculator.py`** - тестирование расчета метрик
- **`test_storage_manager.py`** - тестирование сохранения результатов

#### Интеграционные тесты
- **`test_integration.py`** - полный пайплайн от загрузки до сохранения результатов

### Запуск тестов

```bash
# Запуск всех тестов с отчетом
make test

# Комплексный запуск с анализом покрытия
python run_tests.py

# Запуск только unit тестов
pytest tests/ -v -m "not integration"

# Запуск интеграционных тестов
pytest tests/test_integration.py -v

# Тест с покрытием кода
pytest tests/ --cov=etl --cov-report=html
```

### Метрики тестирования

- **Покрытие кода**: > 80% для всех модулей
- **Время выполнения**: < 10 минут для полного набора тестов
- **Автоматизация**: Интеграция с CI/CD пайплайном

### Стратегия тестирования

1. **Изолированность**: Каждый unit тест независим
2. **Mock объекты**: Для внешних зависимостей (файлы, API, модели)
3. **Граничные случаи**: Тестирование экстремальных значений
4. **Обработка ошибок**: Проверка корректного поведения при ошибках

Подробная документация: [TESTING_STRATEGY.md](TESTING_STRATEGY.md)

## Анализ отказов и устойчивость

### Потенциальные точки сбоя

1. **Источник данных недоступен**
- **Проблема**: Файл данных не найден или поврежден
- **Решение**: Проверка существования файла, валидация формата
- **Airflow**: Retry с экспоненциальной задержкой

2. **Невалидные данные**
- **Проблема**: Неожиданная структура данных, пропущенные значения
- **Решение**: Строгая валидация схемы, обработка исключений
- **Airflow**: Остановка выполнения с детальным логированием

3. **Ошибки обучения модели**
- **Проблема**: Недостаточно данных, проблемы сходимости
- **Решение**: Проверка размера выборки, настройка параметров алгоритма
- **Airflow**: Fallback на базовые параметры модели

4. **Недоступность облачного хранилища**
- **Проблема**: Проблемы с сетью, неверные учетные данные
- **Решение**: Локальное сохранение как fallback, retry механизм
- **Airflow**: Задача не критичная, продолжение выполнения

### Обеспечение устойчивости

#### Логирование
```python
# Структурированное логирование на каждом этапе
logger.info(f"Загружено записей: {len(df)}")
logger.warning(f"Найдено пропущенных значений: {missing_count}")
logger.error(f"Критическая ошибка: {error_message}")
```

#### Обработка исключений
```python
try:
# Критическая операция
result = process_data(data)
except ValidationError as e:
logger.error(f"Данные не прошли валидацию: {e}")
raise
except Exception as e:
logger.error(f"Неожиданная ошибка: {e}")
# Fallback или повторная попытка
```

#### Airflow конфигурация
```python
DEFAULT_ARGS = {
'retries': 2,
'retry_delay': timedelta(minutes=5),
'execution_timeout': timedelta(minutes=30),
'email_on_failure': True,
}
```

#### Валидация данных
```python
def validate_data(df):
issues = []

# Проверка размера
if df.empty:
issues.append("Датасет пустой")

# Проверка обязательных колонок
required_cols = ["id", "diagnosis"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
issues.append(f"Отсутствуют колонки: {missing_cols}")

return len(issues) == 0, issues
```

## Развитие проекта

### Расширенные ETL возможности
- **Feature Engineering**: Автоматическое создание новых признаков на основе существующих
- **Продвинутая обработка выбросов**: Поддержка методов IQR, Z-score и Isolation Forest
- **Отбор признаков**: Univariate selection, RFE и PCA для оптимизации модели
- **Множественные скейлеры**: StandardScaler, RobustScaler, MinMaxScaler

### Интеграция с базами данных
- **SQLite**: Встроенная поддержка для локальной разработки
- **PostgreSQL**: Production-ready интеграция с полной поддержкой ACID
- **MySQL**: Альтернативная реляционная БД для корпоративной среды
- **Автоматическое создание схемы**: Таблицы для экспериментов, предсказаний и качества данных

### Контроль качества данных
- **Комплексные проверки**: Пропущенные значения, дубликаты, выбросы, типы данных
- **Балльная система оценки**: От 0 до 100 баллов с градацией качества
- **Детальная отчетность**: JSON и текстовые отчеты с рекомендациями
- **Мониторинг дрейфа данных**: Статистические тесты для обнаружения изменений в данных

### Улучшенное облачное хранилище
- **Расширенная поддержка S3**: Улучшенная обработка ошибок и retry логика
- **Batch операции**: Массовая загрузка и скачивание файлов
- **Сжатие данных**: Автоматическое сжатие для экономии места и времени
- **Версионирование**: Отслеживание версий моделей и данных

### Краткосрочные улучшения

1. **Расширение алгоритмов ML**
- Добавление Random Forest, SVM, XGBoost
- Ensemble методы
- Автоматический выбор лучшего алгоритма

2. **Улучшение предобработки**
- Feature engineering
- Обработка выбросов с помощью IQR
- Feature selection

3. **Мониторинг модели**
- Drift detection
- Performance monitoring
- A/B тестирование моделей

### Долгосрочные улучшения

1. **MLOps интеграция**
- MLflow для tracking экспериментов
- Model registry
- Automated model deployment

2. **Containerization**
- Docker compose с Airflow
- Kubernetes deployment
- CI/CD пайплайн

3. **Масштабирование**
- Distributed training с Dask
- Spark интеграция для больших данных
- Real-time inference API

4. **Интерфейсы**
- Web UI для запуска пайплайна
- REST API для inference
- Dashboard для мониторинга

## Будущие улучшения и доработки

### Краткосрочные улучшения (1-3 месяца)

#### CI/CD и автоматизация
- **Автоматические тесты**: Интеграция pytest в GitHub Actions с покрытием >90%
- **Автоматическая публикация**: CI/CD для single-repo Docker Hub публикации при тагах
- **Линтинг и форматирование**: pre-commit hooks с black, flake8, mypy
- **Dependency scanning**: Автоматическая проверка уязвимостей в зависимостях

#### Расширение ML возможностей
- **Гиперпараметрическая оптимизация**: Интеграция Optuna/Hyperopt в пайплайн
- **Ensemble методы**: Добавление Random Forest, XGBoost, LightGBM
- **Cross-validation**: Стратифицированная k-fold валидация
- **Feature importance**: Автоматический анализ важности признаков

#### Мониторинг и алерты
- **Prometheus/Grafana**: Метрики производительности модели и системы
- **Data drift detection**: Расширенное отслеживание дрейфа данных
- **Model performance alerts**: Уведомления при деградации модели
- **Health checks**: Автоматические проверки состояния системы

### Среднесрочные улучшения (3-6 месяцев)

#### Облачная интеграция
- **AWS/GCP/Azure**: Полная миграция в облако с managed services
- **Kubernetes**: Развертывание в кластере с автомасштабированием
- **Cloud storage**: S3/GCS для артефактов модели и данных
- **Managed databases**: RDS/Cloud SQL вместо локального PostgreSQL

#### Безопасность и соответствие
- **Secrets management**: Vault/AWS Secrets Manager для паролей и ключей
- **RBAC**: Ролевая система доступа в Airflow
- **Audit logging**: Детальное логирование всех операций
- **GDPR/HIPAA compliance**: Соответствие медицинским стандартам

#### Масштабируемость
- **Distributed training**: MLflow/Kubeflow для распределенного обучения
- **Feature store**: Централизованное хранилище признаков
- **Model registry**: Версионирование и управление моделями
- **A/B testing**: Инфраструктура для тестирования моделей

### Долгосрочные улучшения (6+ месяцев)

#### ML Operations (MLOps)
- **Automated retraining**: Автоматическое переобучение при дрейфе данных
- **Model governance**: Полный жизненный цикл модели с аудитом
- **Explainable AI**: SHAP/LIME для интерпретируемости модели
- **Fairness testing**: Проверка предвзятости модели

#### Медицинская специализация
- **DICOM integration**: Поддержка медицинских изображений
- **Multi-modal ML**: Интеграция текста, изображений, временных рядов
- **Clinical decision support**: Интеграция с медицинскими системами
- **Regulatory compliance**: FDA/CE marking для медицинского ПО

#### Enterprise возможности
- **Multi-tenancy**: Поддержка множественных клиентов/организаций
- **API Gateway**: Централизованное управление API
- **Real-time inference**: Streaming ML для реального времени
- **Backup/DR**: Катастрофоустойчивость и резервное копирование

### Приоритизация улучшений

#### Высокий приоритет
1. **CI/CD pipeline** - критично для production
2. **Мониторинг и алерты** - обнаружение проблем
3. **Гиперпараметрическая оптимизация** - улучшение модели
4. **Автоматические тесты** - качество кода

#### Средний приоритет
1. **Облачная миграция** - масштабируемость
2. **Feature store** - управление признаками
3. **Model registry** - версионирование
4. **Безопасность** - соответствие стандартам

#### Низкий приоритет
1. **Multi-modal ML** - расширение функций
2. **Real-time inference** - дополнительные возможности
3. **Multi-tenancy** - коммерческое развитие
4. **DICOM integration** - специализация

### Идеи инноваций

#### Искусственный интеллект
- **AutoML**: Автоматический выбор алгоритмов и гиперпараметров
- **Neural Architecture Search**: Автоматическое создание архитектур
- **Federated Learning**: Обучение на распределенных данных
- **Transfer Learning**: Использование предобученных моделей

#### Исследования и разработка
- **Quantum ML**: Исследование квантовых алгоритмов
- **Edge computing**: Развертывание на медицинских устройствах
- **Synthetic data**: Генерация синтетических медицинских данных
- **Causal inference**: Причинно-следственный анализ

### Метрики успеха улучшений

| Область | Текущее состояние | Целевые показатели | Сроки |
|---------|-------------------|-------------------|-------|
| **Покрытие тестами** | ~60% | >90% | 1 месяц |
| **Время сборки CI/CD** | Ручная | <5 минут | 2 месяца |
| **Model accuracy** | 97.3% | >98% | 3 месяца |
| **Deployment time** | ~10 минут | <2 минут | 3 месяца |
| **System uptime** | 95% | >99.9% | 6 месяцев |
| **Mean prediction time** | <1s | <100ms | 6 месяцев |

### План реализации по кварталам

#### Q3 2025: Подготовка к проду
- Настройка Docker Hub репозитория
- CI/CD pipeline
- Базовый мониторинг
- Покрытие тестами >90%

#### Q3 2025: ML улучшения
- Оптимизация гиперпараметров
- Ансамблевые модели
- Улучшенные метрики
- Версионирование моделей

#### Q1 2026: Облако и масштабирование
- Переезд в облака
- Работа с безопасностью
- Хранилище признаков
- Автомасштабирование

#### Q2 2026: Специализация
- Медицинский комплаенс
- MLOps практики
- Deep Learning и анализ изображений
- Выход на enterprise уровень

## Разработка

### Настройка окружения разработки

```bash
# Установка dev зависимостей
make dev-install

# Проверка качества кода
make quality

# Запуск тестов
make test

# Генерация документации
make docs
```

### Тестирование

Проект включает комплексную стратегию тестирования с unit и интеграционными тестами.

```bash
# Запуск всех тестов с отчетом
make test

# Комплексный запуск тестов
python run_tests.py

# Запуск только unit тестов
pytest tests/ -v -m "not integration"

# Запуск интеграционных тестов
pytest tests/test_integration.py -v

# Тест с покрытием кода
pytest tests/ --cov=etl --cov-report=html

# Тест конкретного модуля
pytest tests/test_data_loader.py -v
```

## Основные возможности

### Комплексные возможности ETL и интеграции

ML Pipeline включает продвинутые возможности ETL-процесса и интеграции с хранилищами данных:

#### Feature Engineering (Создание признаков)
- **Автоматическое создание композитных признаков**
- **Агрегационные операции** (сумма, среднее, стд. отклонение)
- **Отношения между группами признаков**
- **Интеллектуальная генерация новых признаков**

```python
from etl.data_preprocessor import DataPreprocessor

preprocessor = DataPreprocessor
# Создание новых признаков
df_enhanced = preprocessor.create_feature_engineering(df)
print(f"Создано новых признаков: {len(preprocessor.engineered_features)}")
```

#### Продвинутая обработка выбросов
- **Множественные методы обнаружения**: IQR, Z-score, Isolation Forest
- **Различные стратегии обработки**: удаление, ограничение, трансформация
- **Автоматическая настройка порогов**

```python
# Обнаружение выбросов разными методами
outliers_iqr = preprocessor.detect_outliers(df, method="iqr")
outliers_zscore = preprocessor.detect_outliers(df, method="zscore")
outliers_isolation = preprocessor.detect_outliers(df, method="isolation_forest")

# Обработка выбросов с выбором стратегии
df_clean = preprocessor.handle_outliers(df, method="cap", detection_method="iqr")
```

#### Интеллектуальный отбор признаков
- **Univariate selection** (SelectKBest)
- **Recursive Feature Elimination (RFE)**
- **Principal Component Analysis (PCA)**
- **Автоматический выбор оптимального количества признаков**

```python
# Отбор лучших признаков
X_selected = preprocessor.select_features(X, y, method="univariate", n_features=15)

# RFE с кроссс-валидацией
X_rfe = preprocessor.select_features(X, y, method="rfe", n_features=20)

# PCA для снижения размерности
X_pca = preprocessor.select_features(X, y, method="pca", n_features=10)
```

#### Интеграция с базами данных
- **Поддержка SQLite, PostgreSQL, MySQL**
- **Автоматическое создание схемы таблиц**
- **Сохранение результатов экспериментов**
- **Загрузка и сохранение данных в БД**

```python
from etl.storage_manager import StorageManager

storage = StorageManager

# Создание схемы БД
storage.create_tables_schema

# Сохранение результатов эксперимента
storage.save_experiment_results(
experiment_name="wisconsin_classifier",
model_type="LogisticRegression",
parameters={"C": 1.0, "penalty": "l2"},
metrics={"accuracy": 0.982, "f1_score": 0.981}
)

# Сохранение данных в БД
storage.save_data_to_db(df, table_name="ml_data")

# Загрузка данных из БД
data = storage.load_data_from_db("ml_data", limit=100)
```

#### Комплексный контроль качества данных
- **Автоматическая оценка качества данных**
- **Детальные отчеты с рекомендациями**
- **Интеграция с системой алертов**
- **Мониторинг изменений качества**

```python
from etl.data_quality_controller import DataQualityController

quality_controller = DataQualityController

# Комплексная проверка качества
results = quality_controller.run_comprehensive_checks(df, "dataset_name")
print(f"Общий балл качества: {results['overall_score']}/100")
print(f"Уровень качества: {results['quality_level']}")

# Сохранение отчета
quality_controller.save_quality_report(results, "quality_report.json")
```

#### Мониторинг дрейфа данных
- **Статистические тесты для обнаружения дрейфа**
- **Сравнение распределений признаков**
- **Автоматическое уведомление о критических изменениях**
- **Отслеживание деградации модели**

```python
from etl.data_loader import DataLoader

loader = DataLoader

# Анализ дрейфа между старыми и новыми данными
drift_results = loader.detect_data_drift(df_old, df_new)

if drift_results["summary"]["drift_detected"]:
affected_features = drift_results["summary"]["affected_features"]
print(f"Обнаружен дрейф в {len(affected_features)} признаках")
print(f"Затронутые признаки: {affected_features}")
```

#### Облачная поддержка
- **Интеграция с AWS S3**
- **Поддержка Google Cloud Storage**
- **Автоматическое резервное копирование**
- **Распределенное хранение результатов**

#### Генерация детальных отчетов
- **Комплексные отчеты о качестве данных**
- **Анализ производительности модели**
- **Отчеты по дрейфу данных**
- **Экспорт в различные форматы**

```python
# Генерация полного отчета о качестве данных
detailed_report = loader.generate_data_quality_report(df)
print(f"Общий балл качества: {detailed_report['quality_score']}")
print(f"Количество проблем: {len(detailed_report['data_quality_issues'])}")
print(f"Рекомендации: {len(detailed_report['recommendations'])}")
```

### Команды Makefile

```bash
# Демонстрация всех возможностей
make demo

# Проверка качества данных
make quality-check

# Тестирование feature engineering
make feature-engineering

# Инициализация базы данных
make init-db

# Проверка дрейфа данных
make drift-check

# Установка всех зависимостей
make install-all

# Запуск всех тестов
make test-all
```

> **Совет**: Для получения подробной информации о скачивании образа см. [ Подробное руководство](DOCKER_IMAGE_DOWNLOAD_GUIDE.md)

## Папка docker-images

Проект включает папку `docker-images/` для хранения экспортированных Docker образов в виде файлов.

### Создание файлов образов
```bash
# Экспорт образа в файлы (TAR, TAR.GZ, TAR.XZ)
./export_docker_images.sh

# Публикация + экспорт файлов одной командой
./publish_docker_image.sh latest --export-files
```

### Структура папки
```
docker-images/
README.md # Инструкции по использованию
.gitignore # Игнорирование больших файлов
ml-pipeline-airflow-latest.tar # Образ без сжатия (быстрый импорт)
ml-pipeline-airflow-latest.tar.gz # Образ со сжатием (рекомендуется)
ml-pipeline-airflow-latest.tar.xz # Образ с максимальным сжатием
ml-pipeline-airflow-latest_info.txt # Информация об экспорте
```

### Импорт образа из файлов
```bash
# Рекомендуемый способ (быстро + компактно)
gunzip -c docker-images/ml-pipeline-airflow-latest.tar.gz | docker load

# Самый быстрый импорт (без сжатия)
docker load < docker-images/ml-pipeline-airflow-latest.tar

# Максимальное сжатие (медленнее)
xz -dc docker-images/ml-pipeline-airflow-latest.tar.xz | docker load
```

### Преимущества файлового распространения
- **Офлайн установка** - работает без доступа к Docker реестрам
- **Быстрое развертывание** - локальный импорт быстрее чем pull
- **Контроль версий** - точные версии образов без зависимости от реестров
- **Универсальность** - работает в любой Docker среде

---

## Мультиплатформенная поддержка

Проект поддерживает сборку для нескольких архитектур процессоров:

### Поддерживаемые платформы
- **linux/amd64** - Intel/AMD процессоры (x86_64)
- **linux/arm64** - ARM процессоры (Apple Silicon, Raspberry Pi)

### Мультиплатформенные команды

```bash
# Мультиплатформенная сборка (обе архитектуры)
./build_docker_multiplatform.sh --platforms linux/amd64,linux/arm64 --push

# Мультиплатформенная публикация во все реестры
./publish_docker_image.sh latest --multiplatform

# Публикация с экспортом файлов
./publish_docker_image.sh latest --multiplatform --export-files

# Сборка только для ARM64 (Apple Silicon)
./build_docker_multiplatform.sh --platforms linux/arm64 --push

# Сборка только для AMD64 (Intel/AMD)
./build_docker_multiplatform.sh --platforms linux/amd64 --push
```

### Решение проблемы "Not all multiplatform-content is present"

Если вы видите это сообщение, значит образ собран только для одной архитектуры. Это не ошибка, но можно улучшить совместимость:

```bash
# Вместо обычной сборки
./build_docker_image.sh

# Используйте мультиплатформенную
./publish_docker_image.sh latest --multiplatform
```

### Сравнение режимов сборки

| Режим | Команда | Платформы | Совместимость |
|-------|---------|-----------|---------------|
| **Локальная** | `./build_docker_image.sh` | Текущая | Только ваша архитектура |
| **Одна платформа** | `./build_docker_multiplatform.sh` | Выбранная | Конкретная архитектура |
| **Мультиплатформенная** | `./publish_docker_image.sh --multiplatform` | AMD64 + ARM64 | Максимальная совместимость |

> **Подробное руководство**: [MULTIPLATFORM_BUILD_GUIDE.md](MULTIPLATFORM_BUILD_GUIDE.md)

---

## Single Repository Docker Hub

Проект поддерживает размещение обоих образов (PostgreSQL + Airflow) в одном репозитории Docker Hub с разными тегами.

### Структура single-repo
```
yourusername/ml-pipeline:airflow-latest # Apache Airflow + ML Pipeline
yourusername/ml-pipeline:postgres-latest # PostgreSQL база данных
```

### Сборка и публикация single-repo
```bash
# Сборка обоих образов локально
./build_and_publish_repo.sh

# Сборка и публикация в Docker Hub
./build_and_publish_repo.sh latest --push --username=yourusername

# Запуск с single-repo образами
docker-compose -f docker-compose.single-repo.yml up -d
```

### Преимущества single-repo
- **Связанность** - оба образа в одном месте
- **Простота** - один репозиторий для управления
- **Версионирование** - синхронные версии образов
- **Документация** - единое место для описания

### Использование пользователями
```bash
# Скачивание образов
docker pull yourusername/ml-pipeline:airflow-latest
docker pull yourusername/ml-pipeline:postgres-latest

# Создание .env файла
echo "DOCKER_USERNAME=yourusername" > .env

# Запуск системы
docker-compose -f docker-compose.single-repo.yml up -d
```

---

## Демонстрация и скриншоты

Для демонстрации работы системы используйте папку [`screenshots/`](screenshots/):

### Структура демонстрации:
- ** [setup/](screenshots/setup/)** - Процесс установки и сборки Docker образов
- ** [airflow/](screenshots/airflow/)** - Интерфейс Airflow, DAG, выполнение задач
- ** [results/](screenshots/results/)** - ML результаты: метрики, графики, модели
- ** [database/](screenshots/database/)** - Подключение к PostgreSQL, данные, запросы
- ** [monitoring/](screenshots/monitoring/)** - Мониторинг системы, ресурсы, статус

### Полезные команды для скриншотов:
```bash
# Статус системы
docker ps -a
docker stats --no-stream

# Airflow интерфейс
open http://localhost:8080

# Логи системы
docker logs ml-pipeline-project-airflow-webserver-1

# Подключение к БД
docker exec -it ml-pipeline-project-postgres-1 psql -U ml_user -d ml_pipeline
```

> Подробные инструкции по созданию скриншотов см. в [`screenshots/README.md`](screenshots/README.md)

---

## Дополнительная документация

### Готовые образы и развертывание
- **[ Готовые Docker образы](READY_DOCKER_IMAGES.md)** - Все образы готовы к использованию на Docker Hub
- **[ Обновление Docker Hub](DOCKER_HUB_UPDATE_SUMMARY.md)** - Резюме обновления для использования готовых образов

### Анализ результатов
- **[ Интерпретация результатов](RESULTS_INTERPRETATION.md)** - Комплексный анализ метрик модели ML
- **[ Технический анализ](TECHNICAL_ANALYSIS.md)** - Детальные технические характеристики и математический анализ
- **[ Отчет об оценке](results/evaluation_report.md)** - Краткий отчет с основными метриками

### Визуализации и скриншоты
- **[ Папка скриншотов](screenshots/)** - Организованные скриншоты для демонстрации
- **[ Быстрые команды](screenshots/QUICK_COMMANDS.md)** - Команды для создания скриншотов
- **[ Результаты ML](screenshots/results/)** - Графики метрик, ROC-кривые, матрицы ошибок

### Настройка и развертывание
- **[ Готовые Docker образы](READY_DOCKER_IMAGES.md)** - Все образы готовы к использованию на Docker Hub
- **[ Single-Repo Guide](SINGLE_REPO_GUIDE.md)** - Публикация в один Docker Hub репозиторий
- **[ Статус проекта](PROJECT_STATUS.md)** - Текущее состояние и решенные проблемы
- **[ Конфигурация](config/config.yaml)** - Настройки пайплайна
