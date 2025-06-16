# Single Repository Setup - Changelog

## Исправления (Latest Update)

### Проблема: Неправильная передача аргументов
**Статус**: **ИСПРАВЛЕНО**

#### Что было не так:
- `setup_single_repo.sh` не запрашивал версию у пользователя
- Аргументы передавались в `build_and_publish_repo.sh` без версии
- Это приводило к использованию версии "latest" по умолчанию вместо указанной пользователем

#### Что исправлено:
1. **Добавлен запрос версии в `setup_single_repo.sh`**:
 ```bash
 read -p "Введите версию образов (по умолчанию: latest): " VERSION
 VERSION=${VERSION:-latest}
 ```

2. **Исправлена передача аргументов**:
 ```bash
 # Было:
 ./build_and_publish_repo.sh --username="$DOCKER_USERNAME"

 # Стало:
 ./build_and_publish_repo.sh "$VERSION" --username="$DOCKER_USERNAME"
 ```

3. **Обновлен .env файл**:
 ```bash
 # Теперь версия берется из пользовательского ввода
 VERSION=${VERSION} # вместо hardcoded "latest"
 ```

#### Результат:
- Версия правильно запрашивается и передается
- Теги формируются корректно: `airflow-v1.0.0`, `postgres-v1.0.0`
- Пользователь может указать любую версию
- Интеграционные тесты пройдены

## Проведенные тесты

### 1. Тест парсинга аргументов
```bash
./build_and_publish_repo.sh v1.0.0 --username=testuser
```
**Результат**: Версия и username распознаются корректно

### 2. Интеграционный тест
```bash
# setup_single_repo.sh → build_and_publish_repo.sh
```
**Результат**: Аргументы передаются правильно

### 3. Тест формирования тегов
**Результат**: Теги формируются как ожидается:
- `testuser/mipt-s2-de-ml-pipeline:airflow-v1.0.0`
- `testuser/mipt-s2-de-ml-pipeline:postgres-v1.0.0`

## Готовность к использованию

| Компонент | Статус | Описание |
|-----------|--------|----------|
| `build_and_publish_repo.sh` | | Корректно парсит аргументы |
| `setup_single_repo.sh` | | Правильно передает аргументы |
| `docker-compose.single-repo.yml` | | Использует правильные переменные |
| `.env.example` | | Обновлен для single-repo |
| Документация | | Обновлена и протестирована |

## Готовые команды для пользователей

### Быстрая настройка:
```bash
./setup_single_repo.sh
```

### Ручная сборка:
```bash
# Локальная сборка
./build_and_publish_repo.sh v1.0.0 --username=yourusername

# Публикация в Docker Hub
./build_and_publish_repo.sh v1.0.0 --username=yourusername --push

# Запуск
docker-compose -f docker-compose.single-repo.yml up -d
```

---
**Дата обновления**: $(date)
**Статус**: Готово к продакшн использованию
