#!/bin/bash
# Скрипт для мониторинга и устранения zombie процессов Airflow

echo " Мониторинг Zombie процессов Airflow"
echo ""

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Функция проверки zombie процессов
check_zombie_processes() {
    echo " Проверка zombie процессов..."
    
    # Проверяем zombie в логах scheduler
    if [ -f "$PROJECT_DIR/airflow/logs/scheduler.log" ]; then
        ZOMBIE_COUNT=$(grep -c "Detected zombie job" "$PROJECT_DIR/airflow/logs/scheduler.log" 2>/dev/null || echo "0")
        echo "   Найдено zombie записей в логах: $ZOMBIE_COUNT"
        
        if [ "$ZOMBIE_COUNT" -gt 0 ]; then
            echo "   Последние zombie записи:"
            tail -5 "$PROJECT_DIR/airflow/logs/scheduler.log" | grep "zombie" || echo "   (нет последних записей)"
        fi
    fi
    
    # Проверяем активные процессы Python Airflow
    AIRFLOW_PROCESSES=$(ps aux | grep python | grep airflow | grep -v grep | wc -l | tr -d ' ')
    echo "   Активных процессов Airflow: $AIRFLOW_PROCESSES"
    
    # Проверяем процессы PostgreSQL
    PG_PROCESSES=$(ps aux | grep postgres | grep -v grep | wc -l | tr -d ' ')
    echo "   Процессов PostgreSQL: $PG_PROCESSES"
}

# Функция очистки zombie процессов
cleanup_zombie_processes() {
    echo " Очистка zombie процессов..."
    
    # Находим и завершаем висящие процессы Python с Airflow
    HANGING_PROCESSES=$(ps aux | grep python | grep airflow | grep -v "scheduler\|webserver" | awk '{print $2}')
    
    if [ ! -z "$HANGING_PROCESSES" ]; then
        echo "   Найдены висящие процессы Airflow: $HANGING_PROCESSES"
        for pid in $HANGING_PROCESSES; do
            echo "   Завершаем процесс: $pid"
            kill -9 "$pid" 2>/dev/null || echo "   Не удалось завершить процесс $pid"
        done
    else
        echo "   Висящих процессов не найдено"
    fi
    
    # Очищаем старые временные файлы
    if [ -d "/tmp" ]; then
        find /tmp -name "*airflow*" -type f -mtime +1 -delete 2>/dev/null || true
        echo "   Очищены временные файлы Airflow"
    fi
}

# Функция перезапуска scheduler с улучшенными настройками
restart_scheduler_optimized() {
    echo " Перезапуск scheduler с оптимизированными настройками..."
    
    # Остановка текущего scheduler
    SCHEDULER_PID=$(ps aux | grep "airflow scheduler" | grep -v grep | awk '{print $2}' | head -1)
    if [ ! -z "$SCHEDULER_PID" ]; then
        echo "   Остановка scheduler (PID: $SCHEDULER_PID)..."
        kill -TERM "$SCHEDULER_PID"
        sleep 5
        
        # Если процесс все еще работает, принудительно завершаем
        if ps -p "$SCHEDULER_PID" > /dev/null 2>&1; then
            echo "   Принудительная остановка scheduler..."
            kill -9 "$SCHEDULER_PID"
        fi
    fi
    
    # Активируем окружение
    source "$PROJECT_DIR/venv/bin/activate"
    source "$PROJECT_DIR/airflow_postgresql_env.sh"
    
    # Запускаем scheduler с пониженным приоритетом
    echo "   Запуск scheduler с оптимизациями..."
    nohup nice -n 10 airflow scheduler > "$PROJECT_DIR/airflow/logs/scheduler_optimized.log" 2>&1 &
    NEW_PID=$!
    
    echo "   Новый scheduler запущен с PID: $NEW_PID"
    sleep 5
    
    # Проверяем статус
    if ps -p "$NEW_PID" > /dev/null 2>&1; then
        echo "    Scheduler успешно запущен"
    else
        echo "    Ошибка запуска scheduler"
        return 1
    fi
}

# Функция мониторинга производительности
monitor_performance() {
    echo " Мониторинг производительности..."
    
    # Использование CPU процессами Airflow
    echo "   CPU использование процессами Airflow:"
    ps aux | grep python | grep airflow | grep -v grep | awk '{print "     PID:", $2, "CPU:", $3"%", "MEM:", $4"%", "COMMAND:", $11, $12, $13}'
    
    # Соединения с PostgreSQL
    echo "   Соединения PostgreSQL от Airflow:"
    AIRFLOW_CONNECTIONS=$(psql -U postgres -d airflow_metadata -t -c "SELECT count(*) FROM pg_stat_activity WHERE usename='airflow_user';" 2>/dev/null | tr -d ' ' || echo "Недоступно")
    echo "     Активных соединений: $AIRFLOW_CONNECTIONS"
    
    # Размер логов
    if [ -f "$PROJECT_DIR/airflow/logs/scheduler.log" ]; then
        LOG_SIZE=$(du -h "$PROJECT_DIR/airflow/logs/scheduler.log" | cut -f1)
        echo "   Размер лога scheduler: $LOG_SIZE"
    fi
}

# Функция оптимизации на лету
optimize_runtime() {
    echo " Применение runtime оптимизаций..."
    
    # Установка приоритета для процессов Airflow
    AIRFLOW_PIDS=$(ps aux | grep python | grep airflow | grep -v grep | awk '{print $2}')
    for pid in $AIRFLOW_PIDS; do
        renice 10 "$pid" 2>/dev/null || true
    done
    echo "   Установлен низкий приоритет для процессов Airflow"
    
    # Оптимизация планировщика процессов
    echo "   Применение оптимизаций планировщика..."
    sysctl -w kern.sched.quantum=10000 2>/dev/null || true
}

# Главное меню
case "$1" in
    --check)
        check_zombie_processes
        ;;
    --cleanup)
        cleanup_zombie_processes
        ;;
    --restart)
        restart_scheduler_optimized
        ;;
    --monitor)
        monitor_performance
        ;;
    --optimize)
        optimize_runtime
        ;;
    --full)
        echo " Полная диагностика и оптимизация zombie процессов"
        echo ""
        check_zombie_processes
        echo ""
        cleanup_zombie_processes
        echo ""
        optimize_runtime
        echo ""
        restart_scheduler_optimized
        echo ""
        monitor_performance
        echo ""
        echo " Полная оптимизация завершена"
        ;;
    *)
        echo " Использование:"
        echo "   $0 --check     # Проверить zombie процессы"
        echo "   $0 --cleanup   # Очистить zombie процессы"
        echo "   $0 --restart   # Перезапустить scheduler"
        echo "   $0 --monitor   # Мониторинг производительности"
        echo "   $0 --optimize  # Оптимизация на лету"
        echo "   $0 --full      # Полная диагностика и оптимизация"
        echo ""
        echo " Текущий статус:"
        check_zombie_processes
        ;;
esac

echo ""
echo " Дополнительные команды:"
echo "   tail -f airflow/logs/scheduler.log           # Мониторинг логов scheduler"
echo "   curl -s http://localhost:8080/api/v1/health  # Проверка здоровья Airflow"
echo "   ps aux | grep postgres | grep -v grep | wc -l # Подсчет процессов PostgreSQL"
