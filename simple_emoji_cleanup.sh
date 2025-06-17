#!/bin/bash

echo "=== УДАЛЕНИЕ ЭМОДЗИ ИЗ ПРОЕКТА ==="

# Список файлов с эмодзи
files_with_emojis=(
    "./activate_venv.sh"
    "./setup_airflow_config.py"
    "./reorganize_project.py"
    "./cleanup_project.sh"
    "./FILES_TO_DELETE.md"
    "./cleanup_md_files.sh"
    "./final_emoji_cleanup.py"
)

# Проверим некоторые лог-файлы
log_files=(
    "./logs/scheduler_patched.log"
    "./logs/scheduler_fixed_multiprocessing.log" 
    "./logs/fixed_scheduler_working.log"
    "./logs/fixed_scheduler_v2.log"
    "./logs/fixed_scheduler.log"
)

processed=0

echo "Проверяем основные файлы..."
for file in "${files_with_emojis[@]}"; do
    if [ -f "$file" ]; then
        echo "Обрабатываем: $file"
        
        # Создаем бэкап
        cp "$file" "$file.bak"
        
        # Удаляем эмодзи с помощью sed
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's/👨‍//g' "$file"
        sed -i '' 's///g' "$file"
        
        # Убираем лишние пробелы
        sed -i '' 's/  */ /g' "$file"
        
        echo "  ✓ Обработан: $file"
        processed=$((processed + 1))
    else
        echo "  ! Файл не найден: $file"
    fi
done

echo ""
echo "Проверяем лог-файлы..."
for file in "${log_files[@]}"; do
    if [ -f "$file" ]; then
        echo "Обрабатываем: $file"
        
        # Создаем бэкап
        cp "$file" "$file.bak"
        
        # Удаляем эмодзи (основные)
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        sed -i '' 's///g' "$file"
        
        # Убираем лишние пробелы
        sed -i '' 's/  */ /g' "$file"
        
        echo "  ✓ Обработан: $file"
        processed=$((processed + 1))
    else
        echo "  ! Файл не найден: $file"
    fi
done

echo ""
echo "=== РЕЗУЛЬТАТ ==="
echo "Обработано файлов: $processed"
echo "Резервные копии созданы с расширением .bak"
echo ""
echo "Проверяем результат..."
remaining=$(find . -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.log" | xargs grep -l "\|\|\|\|\|\|\|\|\|\|\|\|" 2>/dev/null | wc -l)
echo "Файлов с эмодзи осталось: $remaining"
