#!/bin/bash

echo " Очистка эмодзи из основных файлов проекта..."
echo

# Счетчики
processed=0
cleaned=0

# Функция для удаления эмодзи из файла
clean_emoji_from_file() {
    local file="$1"
    echo "Обрабатывается: $file"
    
    # Создаем бэкап
    cp "$file" "$file.bak"
    
    # Удаляем эмодзи с помощью sed (macOS версия)
    sed -i '' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' \
        -e 's/👨‍//g' -e 's///g' "$file"
    
    # Проверяем, изменился ли файл
    if ! cmp -s "$file" "$file.bak"; then
        echo "  ✓ Эмодзи удалены"
        rm "$file.bak"
        return 0
    else
        echo "  - Эмодзи не найдены"
        mv "$file.bak" "$file"  # восстанавливаем оригинал
        return 1
    fi
}

echo "Обработка основных файлов проекта..."

# Основные Python файлы
for file in *.py dags/*.py src/*.py etl/*.py tests/*.py; do
    if [[ -f "$file" ]]; then
        ((processed++))
        if clean_emoji_from_file "$file"; then
            ((cleaned++))
        fi
    fi
done

# Shell скрипты
for file in *.sh scripts/*.sh; do
    if [[ -f "$file" ]]; then
        ((processed++))
        if clean_emoji_from_file "$file"; then
            ((cleaned++))
        fi
    fi
done

# Markdown файлы в корне и docs
for file in *.md docs/*.md docs/*/*.md; do
    if [[ -f "$file" ]]; then
        ((processed++))
        if clean_emoji_from_file "$file"; then
            ((cleaned++))
        fi
    fi
done

# Конфигурационные файлы
for file in *.cfg *.yaml *.yml config/*.yaml docker/*.yml; do
    if [[ -f "$file" ]]; then
        ((processed++))
        if clean_emoji_from_file "$file"; then
            ((cleaned++))
        fi
    fi
done

# Основные лог файлы (не в директории logs)
for file in *.log; do
    if [[ -f "$file" ]]; then
        ((processed++))
        if clean_emoji_from_file "$file"; then
            ((cleaned++))
        fi
    fi
done

echo
echo "=== ИТОГИ ==="
echo "Обработано файлов: $processed"
echo "Очищено файлов: $cleaned"
echo "Готово!"
