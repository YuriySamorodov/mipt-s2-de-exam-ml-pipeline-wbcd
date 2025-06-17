#!/bin/bash

echo "Очистка мусорных файлов из проекта..."
echo "ВАЖНО: Скриншоты, логи и результаты останутся нетронутыми"
echo

# Счетчики
total_removed=0
total_size_before=0
total_size_after=0

# Функция для безопасного удаления
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        local size=$(du -k "$file" 2>/dev/null | cut -f1)
        echo "Удаляется: $file (${size}KB)"
        rm "$file"
        total_removed=$((total_removed + 1))
        total_size_before=$((total_size_before + size))
    fi
}

# Функция для удаления директории
safe_remove_dir() {
    local dir="$1"
    if [ -d "$dir" ]; then
        local size=$(du -sk "$dir" 2>/dev/null | cut -f1)
        echo "Удаляется директория: $dir (${size}KB)"
        rm -rf "$dir"
        total_removed=$((total_removed + 1))
        total_size_before=$((total_size_before + size))
    fi
}

echo "=== 1. Удаление backup файлов ==="
find . -name "*.bak" -not -path "./logs/*" -not -path "./results/*" -not -path "./screenshots/*" | while read -r file; do
    safe_remove "$file"
done

find . -name "*.backup*" -not -path "./logs/*" -not -path "./results/*" -not -path "./screenshots/*" | while read -r file; do
    safe_remove "$file"
done

echo
echo "=== 2. Удаление cleanup и emoji скриптов ==="
cleanup_scripts=(
    "./final_cleanup.sh"
    "./clean_project_emojis.sh" 
    "./clean_main_files.sh"
    "./simple_emoji_cleanup.sh"
    "./remove_emojis_bash.sh"
    "./final_emoji_cleanup.py"
    "./remove_emojis.py"
    "./EMOJI_CLEANUP_REPORT.md"
)

for script in "${cleanup_scripts[@]}"; do
    safe_remove "$script"
done

echo
echo "=== 3. Удаление временных Python файлов ==="
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "Удалены файлы Python кэша (.pyc, __pycache__)"

echo
echo "=== 4. Удаление временных файлов редакторов ==="
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.swp" -delete 2>/dev/null  
find . -name "*.swo" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
echo "Удалены временные файлы редакторов"

echo
echo "=== 5. Удаление устаревших fix скриптов ==="
fix_scripts=(
    "./fix_local_executor.sh"
    "./fix_minimal_executor.sh" 
    "./fix_multiprocessing.py"
    "./fixed_local_executor.py"
    "./start_scheduler_fixed.py"
    "./start_scheduler_fixed.sh"
)

for script in "${fix_scripts[@]}"; do
    safe_remove "$script"
done

echo
echo "=== 6. Удаление лишних alias скриптов ==="
alias_scripts=(
    "./alias_start_airflow_docker_8083.sh"
    "./alias_start_airflow_postgres_8082.sh"
    "./alias_start_airflow_sqlite_8081.sh"
    "./wrapper_start_airflow_docker_8083.sh"
    "./wrapper_start_airflow_postgres_8082.sh"
    "./wrapper_start_airflow_sqlite_8081.sh"
)

for script in "${alias_scripts[@]}"; do
    safe_remove "$script"
done

echo
echo "=== 7. Удаление дублированных конфигурационных файлов ==="
duplicate_configs=(
    "./set_absolute_paths_env.py"
    "./start_postgres_scheduler.sh"
    "./start_postgres_stable.sh"
    "./test_sqlite.sh"
)

for config in "${duplicate_configs[@]}"; do
    safe_remove "$config"
done

echo
echo "=== 8. Удаление старых DAG файлов ==="
old_dags=(
    "./dags/test_absolute_paths_dag.py.bak"
)

for dag in "${old_dags[@]}"; do
    safe_remove "$dag"
done

echo
echo "=== 9. Очистка старых скриптов в scripts/ ==="
find ./scripts -name "*fix*" -name "*.py" -o -name "*fix*" -name "*.sh" | head -10 | while read -r file; do
    # Оставляем только основные fix скрипты
    if [[ ! "$file" == *"fix_airflow_config.sh"* ]]; then
        safe_remove "$file"
    fi
done

echo
echo "=== 10. Удаление пустых директорий ==="
find . -type d -empty -not -path "./logs/*" -not -path "./results/*" -not -path "./screenshots/*" -not -path "./.git/*" -delete 2>/dev/null
echo "Удалены пустые директории"

# Подсчет итогового размера
total_size_after=$(du -sk . 2>/dev/null | cut -f1)
saved_space=$((total_size_before))

echo
echo "=== ИТОГИ ОЧИСТКИ ==="
echo "Удалено файлов: $total_removed"
echo "Освобождено места: ${saved_space}KB (~$((saved_space/1024))MB)"
echo
echo "СОХРАНЕНЫ (нетронуты):"
echo "  - logs/ (все логи Airflow)"
echo "  - results/ (результаты ML)"
echo "  - screenshots/ (скриншоты)"
echo "  - data/ (датасеты)"
echo "  - src/ (исходный код)"
echo "  - dags/ (рабочие DAG файлы)"
echo "  - docker/ (Docker конфигурации)"
echo "  - tests/ (тесты)"
echo "  - docs/ (документация)"
echo
echo "Основные рабочие скрипты сохранены:"
echo "  - start-sqlite.sh"
echo "  - start-postgres.sh"  
echo "  - start-docker.sh"
echo "  - activate_venv.sh"
echo
echo "Очистка завершена успешно!"
