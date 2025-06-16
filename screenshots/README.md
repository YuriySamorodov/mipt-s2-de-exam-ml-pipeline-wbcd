# Скриншоты ML Pipeline

Эта папка содержит скриншоты работы ML Pipeline системы для демонстрации функциональности.

## Структура папки

```
screenshots/
 README.md # Этот файл
 setup/ # Скриншоты установки и настройки
 docker-build.png # Процесс сборки Docker образов
 docker-hub-push.png # Публикация на Docker Hub
 docker-compose-up.png # Запуск через docker-compose
 airflow/ # Скриншоты интерфейса Airflow
 dag-overview.png # Обзор DAG
 dag-graph.png # Граф выполнения DAG
 task-logs.png # Логи выполнения задач
 admin-panel.png # Административная панель
 results/ # Скриншоты результатов ML
 model-metrics.png # Метрики модели
 confusion-matrix.png # Матрица ошибок
 roc-curve.png # ROC кривая
 feature-importance.png # Важность признаков
 database/ # Скриншоты базы данных
 postgres-connection.png # Подключение к PostgreSQL
 data-tables.png # Таблицы с данными
 query-results.png # Результаты запросов
 monitoring/ # Скриншоты мониторинга
 system-health.png # Здоровье системы
 resource-usage.png # Использование ресурсов
 error-logs.png # Логи ошибок
```

## Рекомендуемые скриншоты

### 1. Установка и запуск (setup/)
- [ ] Процесс сборки Docker образов
- [ ] Публикация образов на Docker Hub
- [ ] Запуск системы через docker-compose
- [ ] Проверка работающих контейнеров

### 2. Интерфейс Airflow (airflow/)
- [ ] Главная страница с DAG
- [ ] Детальный вид DAG в режиме Graph
- [ ] Логи выполнения задач
- [ ] Административная панель Airflow

### 3. ML результаты (results/)
- [ ] Метрики модели (accuracy, precision, recall, F1)
- [ ] Confusion Matrix (матрица ошибок)
- [ ] ROC кривая и AUC
- [ ] Важность признаков (feature importance)

### 4. База данных (database/)
- [ ] Подключение к PostgreSQL
- [ ] Таблицы с исходными данными
- [ ] Таблицы с результатами предсказаний
- [ ] Примеры SQL запросов

### 5. Мониторинг (monitoring/)
- [ ] Статус контейнеров (docker ps)
- [ ] Использование ресурсов (CPU, память)
- [ ] Логи системы
- [ ] Health check статусы

## Как сделать скриншоты

### Для macOS:
```bash
# Скриншот всего экрана
Cmd + Shift + 3

# Скриншот выделенной области
Cmd + Shift + 4

# Скриншот окна
Cmd + Shift + 4, затем пробел и клик по окну
```

### Для Windows:
```bash
# Скриншот всего экрана
Win + PrtSc

# Скриншот выделенной области
Win + Shift + S
```

### Для Linux:
```bash
# Скриншот всего экрана
gnome-screenshot

# Скриншот выделенной области
gnome-screenshot -a
```

## Команды для демонстрации

### Показать запущенные контейнеры
```bash
docker ps -a
```

### Показать образы
```bash
docker images | grep ml-pipeline
```

### Показать логи
```bash
docker logs ml-pipeline-project-airflow-webserver-1
```

### Показать использование ресурсов
```bash
docker stats
```

## Полезные URL для скриншотов

- **Airflow Web UI**: http://localhost:8080
- **Airflow Admin**: http://localhost:8080/admin
- **Database**: Подключение через pgAdmin или psql
- **Docker Hub**: https://hub.docker.com/r/yourusername/ml-pipeline

## Советы по качеству скриншотов

1. **Разрешение**: Используйте высокое разрешение (минимум 1920x1080)
2. **Формат**: Сохраняйте в PNG для лучшего качества
3. **Описание**: Добавляйте краткое описание в имя файла
4. **Подписи**: При необходимости добавляйте подписи к важным элементам
5. **Последовательность**: Делайте скриншоты в логической последовательности

## Чек-лист для демонстрации

- [ ] Система успешно запущена
- [ ] Все контейнеры работают (healthy)
- [ ] Airflow DAG выполнился успешно
- [ ] Модель обучена и сохранена
- [ ] Метрики рассчитаны и сохранены
- [ ] База данных содержит результаты
- [ ] Логи не показывают критических ошибок
