#!/bin/bash
# Оптимизация PostgreSQL через Homebrew для macOS

echo " Оптимизация Homebrew PostgreSQL для Airflow"
echo ""

# Проверяем установку PostgreSQL через Homebrew
if ! brew list postgresql@14 &> /dev/null; then
    echo "  PostgreSQL@14 не установлен через Homebrew"
    echo "   Рекомендуется переустановить: brew install postgresql@14"
    exit 1
fi

echo " PostgreSQL найден в Homebrew"

# Получаем путь к конфигурации PostgreSQL
PG_CONFIG_DIR=$(brew --prefix postgresql@14)/share/postgresql
PG_DATA_DIR=/usr/local/var/postgresql@14

echo " Конфигурация: $PG_CONFIG_DIR"
echo " Данные: $PG_DATA_DIR"

# Создаем оптимизированную конфигурацию postgresql.conf
cat > "/tmp/postgresql_airflow_optimization.conf" << 'EOF'
# Оптимизация PostgreSQL для Airflow на macOS

# Соединения
max_connections = 100
shared_preload_libraries = ''

# Память
shared_buffers = 128MB
effective_cache_size = 512MB
work_mem = 4MB
maintenance_work_mem = 64MB

# Логирование
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_truncate_on_rotation = on
log_rotation_age = 1d
log_rotation_size = 10MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Производительность
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Очистка
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
EOF

echo " Создана оптимизированная конфигурация PostgreSQL"
echo ""

# Функция применения настроек
apply_pg_optimizations() {
    echo " Остановка PostgreSQL..."
    brew services stop postgresql@14
    
    echo "  Применение оптимизаций..."
    
    # Создаем резервную копию
    cp "$PG_DATA_DIR/postgresql.conf" "$PG_DATA_DIR/postgresql.conf.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Добавляем наши настройки
    cat "/tmp/postgresql_airflow_optimization.conf" >> "$PG_DATA_DIR/postgresql.conf"
    
    echo " Запуск PostgreSQL с новыми настройками..."
    brew services start postgresql@14
    
    echo " Оптимизации PostgreSQL применены!"
    echo " Резервная копия: $PG_DATA_DIR/postgresql.conf.backup.*"
}

# Функция проверки статуса
check_pg_status() {
    echo " Статус PostgreSQL:"
    brew services list | grep postgresql@14
    
    echo ""
    echo " Активные соединения Airflow:"
    psql -U postgres -d airflow_metadata -c "SELECT count(*) as airflow_connections FROM pg_stat_activity WHERE usename='airflow_user';" 2>/dev/null || echo "Не удается подключиться к базе данных"
    
    echo ""
    echo " Использование памяти PostgreSQL:"
    ps aux | grep postgres | head -5
}

# Проверяем аргументы
case "$1" in
    --apply)
        apply_pg_optimizations
        ;;
    --status)
        check_pg_status
        ;;
    --restart)
        echo " Перезапуск PostgreSQL..."
        brew services restart postgresql@14
        sleep 3
        check_pg_status
        ;;
    *)
        echo " Использование:"
        echo "   $0 --apply     # Применить оптимизации"
        echo "   $0 --status    # Проверить статус"
        echo "   $0 --restart   # Перезапустить PostgreSQL"
        echo ""
        echo " Текущий статус:"
        check_pg_status
        ;;
esac

echo ""
echo " Дополнительные команды:"
echo "   brew services start postgresql@14    # Запуск"
echo "   brew services stop postgresql@14     # Остановка"
echo "   brew services restart postgresql@14  # Перезапуск"
echo "   psql -U postgres                      # Подключение к консоли"
