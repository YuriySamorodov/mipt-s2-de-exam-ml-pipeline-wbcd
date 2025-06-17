# Конфигурация gunicorn для стабильной работы Airflow webserver
bind = "0.0.0.0:8081"
workers = 1
worker_class = "sync"
worker_timeout = 600 # Увеличиваем таймаут для длительных задач
worker_connections = 1000
max_requests = 0 # Отключаем перезапуск workers
max_requests_jitter = 0
preload_app = False
timeout = 600 # Увеличиваем общий таймаут
keepalive = 5

# Дополнительные настройки для стабильности
graceful_timeout = 60
max_worker_connections = 1000
worker_tmp_dir = None # Использовать системный tmp
tmp_upload_dir = None
