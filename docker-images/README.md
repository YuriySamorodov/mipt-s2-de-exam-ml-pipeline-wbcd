# Docker Images Export Directory

Эта папка предназначена для хранения экспортированных Docker образов проекта ML Pipeline.

## Использование

### Экспорт образов в файлы
```bash
# Экспорт текущего образа
./export_docker_images.sh

# Экспорт конкретной версии
./export_docker_images.sh v1.0.0
```

### Публикация с экспортом файлов
```bash
# Публикация в реестры + создание файлов
./publish_docker_image.sh latest --export-files
```

## Структура после экспорта

```
docker-images/
 .gitignore # Игнорирование больших файлов
 README.md # Этот файл
 ml-pipeline-airflow-latest.tar # Образ без сжатия
 ml-pipeline-airflow-latest.tar.gz # Образ со сжатием gzip
 ml-pipeline-airflow-latest.tar.xz # Образ с максимальным сжатием
 ml-pipeline-airflow-latest_info.txt # Информация об экспорте
```

## Варианты распространения

### 1. Загрузка на файловый сервер
```bash
# Загрузите .tar.gz файл на ваш веб-сервер
scp docker-images/*.tar.gz user@server:/var/www/downloads/
```

### 2. GitHub Releases
- Перейдите в GitHub Releases вашего репозитория
- Создайте новый релиз
- Загрузите `.tar.gz` файл как asset

### 3. Облачные хранилища
- Google Drive, Dropbox, OneDrive
- Поделитесь публичной ссылкой для скачивания

## Импорт образа пользователями

```bash
# Скачивание и импорт
wget https://your-server.com/ml-pipeline-airflow-latest.tar.gz
gunzip -c ml-pipeline-airflow-latest.tar.gz | docker load

# Проверка
docker images ml-pipeline-airflow:latest
```

## Преимущества файлового распространения

| Преимущество | Описание |
|--------------|----------|
| **Офлайн установка** | Работает без доступа к Docker реестрам |
| **Быстрое развертывание** | Локальный импорт быстрее чем pull |
| **Контроль версий** | Точные версии без зависимости от реестров |
| **Универсальность** | Работает в любой Docker среде |
