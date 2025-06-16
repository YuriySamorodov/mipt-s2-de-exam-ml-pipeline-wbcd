# Обновление: Добавлена папка docker-images

## Новая функциональность

Теперь проект поддерживает **экспорт Docker образов в файлы** для офлайн распространения!

### Быстрый старт

```bash
# 1. Соберите образ
./build_docker.sh

# 2. Экспортируйте в файлы
./export_docker_images.sh

# 3. Или публикуйте + экспортируйте одной командой
./publish_docker_image.sh latest --export-files
```

### Что создается

В папке `docker-images/` появятся файлы:
- `ml-pipeline-airflow-latest.tar` - без сжатия (быстрый импорт)
- `ml-pipeline-airflow-latest.tar.gz` - сжатый (рекомендуется)
- `ml-pipeline-airflow-latest.tar.xz` - максимальное сжатие
- `ml-pipeline-airflow-latest_info.txt` - инструкции

### Преимущества

| Преимущество | Описание |
|--------------|----------|
| **Офлайн установка** | Работает без интернета |
| **Быстрый импорт** | Локальные файлы импортируются быстрее |
| **Портативность** | Можно переносить на флешке |
| **Независимость** | Не зависит от доступности реестров |

### Как распространять

1. **Загрузите на файл-сервер:**
 ```bash
 scp docker-images/*.tar.gz user@server:/downloads/
 ```

2. **GitHub Releases:**
 - Загрузите `.tar.gz` файл в Releases

3. **Облачные хранилища:**
 - Google Drive, Dropbox, OneDrive

### Как пользователи импортируют

```bash
# Скачивание
wget https://your-server.com/ml-pipeline-airflow-latest.tar.gz

# Импорт
gunzip -c ml-pipeline-airflow-latest.tar.gz | docker load

# Запуск
docker-compose up -d
```

## Обновленные команды

```bash
# Новые скрипты
./export_docker_images.sh # Экспорт в файлы
./publish_docker_image.sh --export-files # Публикация + экспорт

# Обновленная документация
docker-images/README.md # Инструкции по файлам
DOCKER_IMAGE_PUBLISHING_GUIDE.md # Обновленное руководство
```

Теперь ваш проект поддерживает **4 способа распространения** Docker образов:
1. Docker Hub
2. GitHub Container Registry
3. Файлы образов
4. Локальная сборка
