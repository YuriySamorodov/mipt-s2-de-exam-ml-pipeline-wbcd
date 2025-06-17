#!/bin/bash

echo "=== ОЧИСТКА И РЕОРГАНИЗАЦИЯ ПРОЕКТА ==="
echo

# Создаем директории если их нет
mkdir -p scripts/cleanup
mkdir -p scripts/utilities

echo "1. Перемещение вспомогательных .sh файлов в scripts..."

# Файлы для очистки эмодзи -> scripts/cleanup
sh_cleanup_files=(
    "clean_main_files.sh"
    "clean_project_emojis.sh" 
    "final_cleanup.sh"
    "remove_emojis_bash.sh"
    "simple_emoji_cleanup.sh"
)

for file in "${sh_cleanup_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Перемещаем $file -> scripts/cleanup/"
        mv "$file" scripts/cleanup/
    fi
done

# Вспомогательные файлы -> scripts/utilities
sh_utility_files=(
    "fix_local_executor.sh"
    "fix_minimal_executor.sh"
    "start_postgres_scheduler.sh"
    "start_postgres_stable.sh"
    "start_scheduler_fixed.sh"
    "airflow_start_guide.sh"
)

for file in "${sh_utility_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Перемещаем $file -> scripts/utilities/"
        mv "$file" scripts/utilities/
    fi
done

# Alias и wrapper файлы -> scripts/
alias_files=(
    "alias_start_airflow_docker_8083.sh"
    "alias_start_airflow_postgres_8082.sh"
    "alias_start_airflow_sqlite_8081.sh"
    "wrapper_start_airflow_docker_8083.sh"
    "wrapper_start_airflow_postgres_8082.sh"
    "wrapper_start_airflow_sqlite_8081.sh"
)

for file in "${alias_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Перемещаем $file -> scripts/"
        mv "$file" scripts/
    fi
done

echo
echo "2. Перемещение вспомогательных .py файлов в scripts..."

# Python файлы для очистки -> scripts/cleanup
py_cleanup_files=(
    "final_emoji_cleanup.py"
    "remove_emojis.py"
)

for file in "${py_cleanup_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Перемещаем $file -> scripts/cleanup/"
        mv "$file" scripts/cleanup/
    fi
done

# Python утилиты -> scripts/utilities
py_utility_files=(
    "fix_multiprocessing.py"
    "fixed_local_executor.py"
    "start_scheduler_fixed.py"
    "set_absolute_paths_env.py"
)

for file in "${py_utility_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Перемещаем $file -> scripts/utilities/"
        mv "$file" scripts/utilities/
    fi
done

echo
echo "3. Удаление backup файлов..."

# Удаляем backup файлы (НЕ в директориях logs, results, screenshots)
backup_files_to_remove=(
    "activate_venv.sh.backup.*"
    "*.backup.*"
    "*.bak"
    "*.old"
    "*.tmp"
)

for pattern in "${backup_files_to_remove[@]}"; do
    # Ищем только в корне проекта, исключая logs, results, screenshots
    find . -maxdepth 1 -name "$pattern" -type f | while read -r file; do
        echo "  Удаляем: $file"
        rm -f "$file"
    done
done

# Удаляем backup файлы в dags (кроме основных)
find ./dags -name "*.bak" -type f | while read -r file; do
    echo "  Удаляем: $file"
    rm -f "$file"
done

echo
echo "4. Удаление временных отчетов..."

# Удаляем временные отчеты (оставляем важные)
temp_reports=(
    "EMOJI_CLEANUP_REPORT.md"
    "cleanup_project_files.sh"
)

for file in "${temp_reports[@]}"; do
    if [ -f "$file" ]; then
        echo "  Удаляем: $file"
        rm -f "$file"
    fi
done

echo
echo "5. Очистка пустых директорий..."

# Удаляем пустую директорию etl в корне (если есть)
if [ -d "etl" ] && [ -z "$(ls -A etl 2>/dev/null)" ]; then
    echo "  Удаляем пустую директорию: etl/"
    rmdir etl
fi

echo
echo "6. Очистка дублированных файлов в scripts..."

# Удаляем дублированные файлы в scripts если они уже есть в других местах
scripts_duplicates=(
    "scripts/activate_venv.sh"  # уже есть в корне
)

for file in "${scripts_duplicates[@]}"; do
    if [ -f "$file" ]; then
        echo "  Удаляем дубликат: $file"
        rm -f "$file"
    fi
done

echo
echo "=== ИТОГИ ОЧИСТКИ ==="
echo "✓ Перемещены .sh файлы в scripts/"
echo "✓ Перемещены .py утилиты в scripts/"
echo "✓ Удалены backup файлы"
echo "✓ Удалены временные отчеты"
echo "✓ Очищены пустые директории"
echo "✓ Удалены дубликаты"
echo
echo "СОХРАНЕНЫ (нетронуты):"
echo "- logs/ (все логи)"
echo "- results/ (результаты)"
echo "- screenshots/ (скриншоты)"
echo "- Основные скрипты запуска (start-*.sh, test_sqlite.sh, activate_venv.sh)"
echo "- Все важные конфигурационные файлы"
echo
echo "НОВАЯ СТРУКТУРА scripts/:"
echo "scripts/"
echo "├── cleanup/          # Скрипты очистки эмодзи"
echo "├── utilities/        # Вспомогательные утилиты"
echo "├── alias_*.sh        # Алиасы запуска"
echo "└── wrapper_*.sh      # Обертки запуска"
