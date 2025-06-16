#!/bin/bash
# Оптимизация PostgreSQL для macOS + Airflow

echo " Оптимизация PostgreSQL для устранения zombie процессов"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Создаем улучшенную конфигурацию airflow.cfg
cat > "$PROJECT_DIR/airflow_optimized.cfg.patch" << 'EOF'
# Оптимизированные настройки для macOS + PostgreSQL

[database]
# Пулинг соединений для уменьшения количества процессов PostgreSQL
sql_alchemy_pool_size = 5
sql_alchemy_pool_recycle = 3600
sql_alchemy_pool_pre_ping = True
sql_alchemy_max_overflow = 10

# Таймауты соединений
sql_alchemy_connect_args = {"connect_timeout": 60}

[scheduler]
# Увеличенные интервалы для снижения нагрузки
job_heartbeat_sec = 30
scheduler_heartbeat_sec = 30
local_task_job_heartbeat_sec = 60
scheduler_zombie_task_threshold = 900
zombie_detection_interval = 120.0

# Ограничение параллельности
max_active_runs_per_dag = 1
max_active_tasks_per_dag = 4

[core]
# Ограничение параллельности
parallelism = 8
max_active_tasks_per_dag = 4
max_active_runs_per_dag = 1

# Таймауты задач
task_timeout = 300
dagbag_import_timeout = 60

[webserver]
# Оптимизация веб-сервера
workers = 1
worker_timeout = 300
worker_class = sync
EOF

echo " Создан файл оптимизации: airflow_optimized.cfg.patch"
echo ""
echo " Применение оптимизаций:"
echo ""

# Функция применения настроек
apply_optimizations() {
    local cfg_file="$PROJECT_DIR/airflow/airflow.cfg"
    
    if [ ! -f "$cfg_file" ]; then
        echo " Файл airflow.cfg не найден: $cfg_file"
        return 1
    fi
    
    echo "  Применение оптимизаций к $cfg_file..."
    
    # Создаем резервную копию
    cp "$cfg_file" "$cfg_file.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Применяем настройки пулинга соединений
    sed -i '' 's/^# sql_alchemy_pool_size = .*/sql_alchemy_pool_size = 5/' "$cfg_file"
    sed -i '' 's/^# sql_alchemy_pool_recycle = .*/sql_alchemy_pool_recycle = 3600/' "$cfg_file"
    sed -i '' 's/^# sql_alchemy_pool_pre_ping = .*/sql_alchemy_pool_pre_ping = True/' "$cfg_file"
    sed -i '' 's/^# sql_alchemy_max_overflow = .*/sql_alchemy_max_overflow = 10/' "$cfg_file"
    
    # Применяем настройки планировщика (уже сделано ранее)
    echo " Оптимизации применены!"
    echo " Резервная копия сохранена: $cfg_file.backup.*"
}

# Проверяем, нужно ли применить оптимизации
if [ "$1" = "--apply" ]; then
    apply_optimizations
else
    echo " Для применения оптимизаций выполните:"
    echo "   $0 --apply"
fi

echo ""
echo " Дополнительные рекомендации:"
echo ""
echo "1.  Мониторинг соединений PostgreSQL:"
echo "   SELECT count(*) FROM pg_stat_activity WHERE usename='airflow_user';"
echo ""
echo "2.  Очистка старых соединений:"
echo "   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE usename='airflow_user' AND state='idle in transaction';"
echo ""
echo "3.  Проверка производительности:"
echo "   ps aux | grep postgres | wc -l"
echo ""
echo "4.  Перезапуск PostgreSQL (если нужно):"
echo "   brew services restart postgresql"
