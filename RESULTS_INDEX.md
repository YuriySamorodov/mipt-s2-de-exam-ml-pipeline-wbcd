# Индекс результатов ML Pipeline

> **Навигация по всем результатам и анализам системы диагностики рака молочной железы**

---

## Краткие результаты

### Ключевые метрики:
- **Точность**: 97.37%
- **Чувствительность**: 95.24% (обнаружение рака)
- **Специфичность**: 98.61% (исключение рака)
- **ROC-AUC**: 99.60% (практически идеальная классификация)

---

## Документы и отчеты

### Основные анализы
| Документ | Описание | Целевая аудитория |
|----------|----------|-------------------|
| **[ RESULTS_INTERPRETATION.md](RESULTS_INTERPRETATION.md)** | Комплексная интерпретация результатов | Врачи, исследователи, менеджеры |
| **[ TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)** | Детальный технический анализ | ML-инженеры, Data Scientists |
| **[ evaluation_report.md](results/evaluation_report.md)** | Краткий отчет с метриками | Быстрый обзор |

### Специализированные отчеты
| Файл | Содержание | Формат |
|------|------------|--------|
| `comprehensive_demo_report.json` | Полный отчет о качестве данных | JSON |
| `final_metrics_*.json` | Метрики производительности модели | JSON |
| `pipeline_results_*.json` | Результаты всего пайплайна | JSON |

---

## Визуализации

### Основные графики
| Изображение | Описание | Расположение |
|-------------|----------|--------------|
| **confusion_matrix.png** | Матрица ошибок классификации | `results/` & `screenshots/results/` |
| **roc_curve.png** | ROC-кривая (AUC = 99.60%) | `results/` & `screenshots/results/` |
| **precision_recall_curve.png** | Precision-Recall кривая | `results/` & `screenshots/results/` |

### Скриншоты системы
| Категория | Папка | Содержание |
|-----------|-------|------------|
| **Setup** | `screenshots/setup/` | Установка, сборка Docker |
| **Airflow** | `screenshots/airflow/` | Интерфейс, DAG, задачи |
| **Results** | `screenshots/results/` | ML результаты, графики |
| **Database** | `screenshots/database/` | PostgreSQL, данные |
| **Monitoring** | `screenshots/monitoring/` | Системные метрики |

---

## Структура файлов результатов

```
results/
 Метрики и отчеты
 final_metrics_YYYYMMDD_HHMMSS.json # Метрики модели
 comprehensive_demo_report.json # Отчет о данных
 evaluation_report.md # Краткий отчет
 pipeline_results_YYYYMMDD_HHMMSS.json # Результаты пайплайна

 Модели
 final_model_YYYYMMDD_HHMMSS.joblib # Обученная модель
 models/ # Дополнительные модели

 Визуализации
 confusion_matrix.png # Матрица ошибок
 roc_curve.png # ROC-кривая
 precision_recall_curve.png # PR-кривая

 Архивы
 ml_pipeline_results_YYYYMMDD_HHMMSS.zip # Архив результатов
 demo_results.zip # Демо результаты

 Вспомогательные
 data_analysis.json # Анализ данных
 save_summary_YYYYMMDD_HHMMSS.json # Сводка сохранения
 logs/ # Логи выполнения
```

---

## Быстрый доступ к результатам

### Последние метрики (JSON)
```bash
# Самые свежие метрики
cat results/final_metrics_20250616_025853.json

# Краткий отчет
cat results/evaluation_report.md

# Качество данных
cat results/comprehensive_demo_report.json
```

### Просмотр визуализаций
```bash
# Открыть графики
open results/confusion_matrix.png
open results/roc_curve.png
open results/precision_recall_curve.png

# Или из папки скриншотов
open screenshots/results/
```

---

## Рекомендуемый порядок изучения

### 1. Быстрый старт
1. **[evaluation_report.md](results/evaluation_report.md)** - краткий обзор
2. **[confusion_matrix.png](results/confusion_matrix.png)** - визуальная оценка

### 2. Подробный анализ
3. **[RESULTS_INTERPRETATION.md](RESULTS_INTERPRETATION.md)** - полная интерпретация
4. **[roc_curve.png](results/roc_curve.png)** & **[precision_recall_curve.png](results/precision_recall_curve.png)**

### 3. Техническая экспертиза
5. **[TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)** - глубокий технический анализ
6. **[final_metrics_*.json](results/)** - исходные данные для анализа

### 4. Демонстрация
7. **[screenshots/](screenshots/)** - скриншоты для презентаций
8. **[QUICK_COMMANDS.md](screenshots/QUICK_COMMANDS.md)** - команды для демо

---

## Контакты и поддержка

### Техническая поддержка
- **Исходный код**: `ml-pipeline-project/`
- **Конфигурация**: `config/config.yaml`
- **Логи**: `results/logs/`

### Документация
- **README**: [README.md](README.md) - основная документация
- **Настройка**: [SINGLE_REPO_GUIDE.md](SINGLE_REPO_GUIDE.md)
- **Статус**: [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

## Версионирование

- **Модель**: Версия от 2025-06-16 02:58:38
- **Данные**: Hash `3899dcdd1ed749f9`
- **Pipeline**: Последний успешный запуск 16.06.2025
- **Документация**: Обновлена 16.06.2025

---

*Данный индекс автоматически генерируется системой ML Pipeline*
*Для получения актуальной информации запустите пайплайн заново*

 **[Вернуться к основной документации](README.md)**
