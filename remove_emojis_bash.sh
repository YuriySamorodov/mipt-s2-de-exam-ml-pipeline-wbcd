#!/bin/bash

# Скрипт для удаления всех эмодзи из файлов проекта

echo " Начинаем очистку эмодзи из проекта..."

# Список всех эмодзи для удаления
EMOJIS=(
    "" "" "" "" "" "" "" "" "" "" "" ""
    "" "" "" "" "" "" "" "" "" "" "" ""
    "" "" "" "" "" "" "" "" "" "" "" ""
    "" "" "" "" "" "" "" "" "" "" "🔌" "🗄️"
    "" "" "" "" "📯" "📍" "📇" "🎖️" "🎺" "📲"
    "🔔" "🔕" "📢" "📣" "🔖" "🏷️" "📮" "🗳️" "✏️" "✒️"
    "🖋️" "🖊️" "🖌️" "🖍️" "📒" "📓" "📔" "📕" "📗" "📘" "📙"
    "📚" "📰" "🗞️" "📃" "📜" "" "📉" "🗒️" "🗓️"
    "📆" "🗑️" "📎" "🖇️" "📐" "📏" "🗃" "🗄" "🗂" "🗑"
    "🔓" "🔏" "🔐" "👨‍" ""
)

# Функция для создания резервной копии
backup_file() {
    local file="$1"
    cp "$file" "$file.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   Создана резервная копия: $file.backup.$(date +%Y%m%d_%H%M%S)"
}

# Функция для удаления эмодзи из файла
clean_emojis_from_file() {
    local file="$1"
    local changed=false
    
    # Проверяем, есть ли эмодзи в файле
    for emoji in "${EMOJIS[@]}"; do
        if grep -q "$emoji" "$file" 2>/dev/null; then
            changed=true
            break
        fi
    done
    
    if [ "$changed" = true ]; then
        echo " Обрабатываем: $file"
        
        # Создаем резервную копию
        backup_file "$file"
        
        # Удаляем каждый эмодзи
        for emoji in "${EMOJIS[@]}"; do
            sed -i '' "s/$emoji//g" "$file"
        done
        
        # Убираем лишние пробелы
        sed -i '' 's/  \+/ /g' "$file"  # множественные пробелы
        sed -i '' 's/^ \+//g' "$file"   # пробелы в начале строк
        
        echo "   Файл очищен"
        return 0
    fi
    
    return 1
}

# Счетчики
total_files=0
processed_files=0

# Находим все текстовые файлы (исключаем этот скрипт и бэкапы)
echo " Поиск файлов с эмодзи..."

find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.txt" -o -name "*.cfg" -o -name "*.yaml" -o -name "*.yml" -o -name "*.log" \) \
    ! -name "remove_emojis_bash.sh" \
    ! -name "*.backup.*" \
    ! -path "./venv/*" \
    ! -path "./.git/*" \
    ! -path "./__pycache__/*" \
    ! -path "./node_modules/*" \
    | while read -r file; do
    
    total_files=$((total_files + 1))
    
    if clean_emojis_from_file "$file"; then
        processed_files=$((processed_files + 1))
    fi
done

echo ""
echo " ОЧИСТКА ЗАВЕРШЕНА!"
echo " Статистика:"
echo "   Всего файлов проверено: $total_files"
echo "   Файлов с эмодзи обработано: $processed_files"
echo ""
echo " Резервные копии сохранены с расширением .backup.YYYYMMDD_HHMMSS"
echo "🗑️  Для удаления резервных копий используйте: find . -name '*.backup.*' -delete"
