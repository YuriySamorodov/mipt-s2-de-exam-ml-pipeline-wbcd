#!/bin/bash

echo "=== ФИНАЛЬНАЯ ОЧИСТКА ЭМОДЗИ ==="

# Функция для удаления эмодзи из файла
remove_emojis() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        echo "Файл не найден: $file"
        return 1
    fi
    
    echo "Очистка: $file"
    
    # Создаем резервную копию если ее еще нет
    if [ ! -f "$file.clean.bak" ]; then
        cp "$file" "$file.clean.bak"
    fi
    
    # Удаляем все Unicode символы эмодзи одной командой
    # Используем Perl для более надежного удаления Unicode
    perl -i -pe 's/[\x{1F600}-\x{1F64F}]//g; # Emoticons
                  s/[\x{1F300}-\x{1F5FF}]//g; # Symbols & Pictographs
                  s/[\x{1F680}-\x{1F6FF}]//g; # Transport & Map
                  s/[\x{1F1E0}-\x{1F1FF}]//g; # Flags
                  s/[\x{2600}-\x{26FF}]//g;   # Miscellaneous Symbols
                  s/[\x{2700}-\x{27BF}]//g;   # Dingbats
                  s/[\x{1F900}-\x{1F9FF}]//g; # Supplemental Symbols
                  s/[\x{1FA70}-\x{1FAFF}]//g; # Extended-A
                  s/[\x{2B05}-\x{2B07}]//g;   # Arrows
                  s/\s+/ /g;                   # Multiple spaces to single
                  s/^\s+//gm;                  # Leading spaces' "$file"
    
    echo "  ✓ Очищен"
}

# Список основных файлов для очистки
main_files=(
    "activate_venv.sh"
    "setup_airflow_config.py" 
    "reorganize_project.py"
    "cleanup_project.sh"
    "FILES_TO_DELETE.md"
    "cleanup_md_files.sh"
)

# Обрабатываем основные файлы
echo "Обрабатываем основные файлы..."
for file in "${main_files[@]}"; do
    if [ -f "$file" ]; then
        remove_emojis "$file"
    fi
done

# Ищем и обрабатываем все .log файлы с эмодзи
echo ""
echo "Обрабатываем лог-файлы..."
find ./logs -name "*.log" -exec grep -l "[\x{1F600}-\x{1F64F}\x{1F300}-\x{1F5FF}\x{1F680}-\x{1F6FF}]" {} \; 2>/dev/null | while read -r logfile; do
    remove_emojis "$logfile"
done

# Проверяем результат
echo ""
echo "=== ПРОВЕРКА РЕЗУЛЬТАТА ==="

remaining_files=0
for file in "${main_files[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "\|\|\|\|\|\|\|\|\|\|\|\|" "$file" 2>/dev/null; then
            echo "  Эмодзи остались в: $file"
            remaining_files=$((remaining_files + 1))
        else
            echo "✓ Очищен: $file"
        fi
    fi
done

echo ""
if [ $remaining_files -eq 0 ]; then
    echo " ВСЕ ЭМОДЗИ УСПЕШНО УДАЛЕНЫ!"
else
    echo "  Эмодзи остались в $remaining_files файлах"
fi

echo ""
echo "Резервные копии сохранены с расширением .clean.bak"
