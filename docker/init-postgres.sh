#!/bin/bash
# Скрипт инициализации PostgreSQL для ML Pipeline

set -e

echo " Инициализация PostgreSQL для ML Pipeline..."

# Создание дополнительных таблиц или настроек если нужно
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Создание схемы для ML Pipeline (если нужно)
    CREATE SCHEMA IF NOT EXISTS ml_pipeline;
    
    -- Предоставление прав пользователю airflow
    GRANT ALL PRIVILEGES ON SCHEMA ml_pipeline TO $POSTGRES_USER;
    
    -- Создание расширений
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Оптимизация для Airflow
    ALTER SYSTEM SET max_connections = 200;
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET effective_cache_size = '1GB';
    ALTER SYSTEM SET work_mem = '8MB';
    
    SELECT pg_reload_conf();
EOSQL

echo " PostgreSQL инициализирован для ML Pipeline"
