# Руководство по мультиплатформенной сборке Docker

## Что такое мультиплатформенные образы

Мультиплатформенные Docker образы поддерживают несколько архитектур процессоров:
- **linux/amd64** - для Intel/AMD процессоров (x86_64)
- **linux/arm64** - для ARM процессоров (Apple Silicon, Raspberry Pi)

## Решение проблемы "Not all multiplatform-content is present"

Ваше сообщение означает, что образ собран только для одной платформы. Это не ошибка, но можно улучшить совместимость.

## Быстрый старт

### 1. Проверка поддержки Buildx
```bash
# Проверка наличия buildx
docker buildx version

# Просмотр доступных builder'ов
docker buildx ls
```

### 2. Мультиплатформенная сборка
```bash
# Создание мультиплатформенного образа (без загрузки локально)
./build_docker_multiplatform.sh --platforms linux/amd64,linux/arm64 --push

# Сборка только для текущей платформы (с загрузкой локально)
./build_docker_multiplatform.sh
```

### 3. Публикация мультиплатформенного образа
```bash
# Сборка и публикация в несколько реестров
./publish_docker_image.sh latest --multiplatform

# С экспортом файлов
./publish_docker_image.sh latest --multiplatform --export-files
```

## Доступные команды

### Локальная сборка (одна платформа)
```bash
# Для текущей архитектуры
./build_docker_image.sh

# Мультиплатформенный скрипт (одна платформа с загрузкой)
./build_docker_multiplatform.sh
```

### Мультиплатформенная сборка
```bash
# Обе основные платформы
./build_docker_multiplatform.sh --platforms linux/amd64,linux/arm64 --push

# Только AMD64
./build_docker_multiplatform.sh --platforms linux/amd64 --push

# Только ARM64
./build_docker_multiplatform.sh --platforms linux/arm64 --push
```

### Публикация
```bash
# Локальный образ (одна платформа)
./publish_docker_image.sh

# Мультиплатформенная публикация
./publish_docker_image.sh --multiplatform

# С кастомными платформами
./publish_docker_image.sh --multiplatform --platforms=linux/amd64,linux/arm64
```

## Сравнение режимов

| Режим | Команда | Платформы | Загрузка локально | Публикация |
|-------|---------|-----------|-------------------|------------|
| **Локальная сборка** | `./build_docker_image.sh` | Текущая | Да | Через отдельный скрипт |
| **Одна платформа** | `./build_docker_multiplatform.sh` | Текущая | Да | Через отдельный скрипт |
| **Мультиплатформенная** | `./build_docker_multiplatform.sh --platforms ... --push` | Множественные | Нет | Сразу |
| **Авто-публикация** | `./publish_docker_image.sh --multiplatform` | AMD64+ARM64 | Нет | Во все реестры |

## Настройка Docker Buildx

### Создание нового builder
```bash
# Создание builder с поддержкой эмуляции
docker buildx create --name multiplatform-builder --driver docker-container --use

# Запуск и проверка
docker buildx inspect --bootstrap
```

### Установка эмуляторов (если нужно)
```bash
# Установка qemu для эмуляции других архитектур
docker run --privileged --rm tonistiigi/binfmt --install all

# Проверка поддержки платформ
docker buildx ls
```

## Быстрые сценарии

### Разработка (быстро)
```bash
# Сборка только для текущей платформы
./build_docker_image.sh
```

### Тестирование на разных архитектурах
```bash
# Мультиплатформенная сборка с публикацией
./build_docker_multiplatform.sh --platforms linux/amd64,linux/arm64 --push
```

### Production публикация
```bash
# Полная мультиплатформенная публикация во все реестры
./publish_docker_image.sh latest --multiplatform --export-files
```

## Troubleshooting

### Ошибка: "buildx not found"
```bash
# Обновите Docker Desktop или установите buildx plugin
# Для Linux:
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/buildx/releases/latest/download/buildx-v0.11.2.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx
```

### Медленная сборка ARM64 на AMD64
```bash
# Это нормально - используется эмуляция
# Для ускорения используйте только нужные платформы:
./build_docker_multiplatform.sh --platforms linux/amd64 --push
```

### Нельзя загрузить мультиплатформенный образ локально
```bash
# Docker не может загрузить образ для нескольких платформ одновременно
# Используйте --push для отправки в реестр или соберите для одной платформы
./build_docker_multiplatform.sh --platforms linux/amd64 --load
```

## Рекомендации

1. **Для разработки**: используйте локальную сборку (`./build_docker_image.sh`)
2. **Для публикации**: используйте мультиплатформенную сборку (`--multiplatform`)
3. **Для максимальной совместимости**: поддерживайте обе платформы (AMD64 + ARM64)
4. **Для экономии времени**: собирайте только нужные платформы
