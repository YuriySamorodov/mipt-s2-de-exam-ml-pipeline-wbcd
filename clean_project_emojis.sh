#!/bin/bash

echo " Очистка эмодзи из проектных файлов..."
echo

# Функция для удаления эмодзи из файла
clean_emoji_from_file() {
    local file="$1"
    echo "Обрабатывается: $file"
    
    # Создаем временный файл
    local temp_file=$(mktemp)
    
    # Удаляем эмодзи с помощью sed
    # Основные эмодзи диапазоны в UTF-8
    sed -E 's/[🀀-🿿]//g; s/[⚀-⛿]//g; s/[✀-➿]//g; s/[-🔿]//g; s/[📀-📿]//g; s/[🎀-🎿]//g; s/[🏀-🏿]//g; s/[🐀-🐿]//g; s/[👀-👿]//g; s/[💀-💿]//g; s/[-🚿]//g; s/[🤀-🤿]//g; s/[🥀-🥿]//g; s/[🦀-🦿]//g; s/[🧀-🧿]//g; s/[🨀-🨿]//g; s/[🩀-🩿]//g; s/[🪀-🪿]//g; s/[🫀-🫿]//g' "$file" > "$temp_file"
    
    # Дополнительно удаляем конкретные эмодзи
    sed -i '' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' -e 's///g' "$temp_file"
    
    # Проверяем, изменился ли файл
    if ! cmp -s "$file" "$temp_file"; then
        cp "$temp_file" "$file"
        echo "  ✓ Эмодзи удалены"
    else
        echo "  - Эмодзи не найдены"
    fi
    
    rm "$temp_file"
}

# Счетчики
processed=0
cleaned=0

echo "Поиск проектных файлов..."

# Находим файлы проекта, исключая импортированные директории
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.txt" -o -name "*.cfg" -o -name "*.yaml" -o -name "*.yml" -o -name "*.log" \) \
    -not -path "./.venv/*" \
    -not -path "./venv/*" \
    -not -path "./__pycache__/*" \
    -not -path "./node_modules/*" \
    -not -path "./.git/*" \
    -not -path "./airflow/logs/*" \
    -not -path "./logs/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./build/*" \
    -not -path "./dist/*" \
    -not -path "./*.egg-info/*" \
    -not -name "*.pyc" \
    -not -name "*.pyo" \
    -not -name "*.db" \
    -not -name "*.sqlite" \
    -not -name "*.backup" | while read -r file; do
    
    processed=$((processed + 1))
    
    # Проверяем, есть ли эмодзи в файле
    if grep -q '[🀀-🿿⚀-⛿✀-➿]' "$file" 2>/dev/null; then
        clean_emoji_from_file "$file"
        cleaned=$((cleaned + 1))
    fi
done

echo
echo "=== ИТОГИ ==="
echo "Обработано файлов: $processed"
echo "Очищено файлов: $cleaned"
echo "Готово!"
