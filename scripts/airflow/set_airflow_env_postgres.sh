#!/bin/bash
# Автоматически сгенерированный скрипт с переменными окружения Airflow
# Все пути программно сформированы как абсолютные
# Режим развертывания: PostgreSQL (порт 8082)

echo " Установка переменных окружения Airflow с абсолютными путями..."
echo " Режим: PostgreSQL (порт 8082)"

# Экспорт переменных окружения
export AIRFLOW_HOME="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/dags"
export AIRFLOW__CORE__PLUGINS_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/plugins"
export AIRFLOW__LOGGING__BASE_LOG_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/logs"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
export AIRFLOW__WEBSERVER__SECRET_KEY="dev_secret_key_for_postgres"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8082"
export AIRFLOW__CORE__CHECK_SLAS="False"
export AIRFLOW__CORE__STORE_SERIALIZED_DAGS="True"
export AIRFLOW__CORE__STORE_DAG_CODE="True"
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG="True"
export AIRFLOW__WEBSERVER__WORKERS="4"
export AIRFLOW__WEBSERVER__WORKER_TIMEOUT="300"

echo " Переменные окружения установлены:"
echo " Проект: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow"
echo " AIRFLOW_HOME: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/airflow"
echo " DAGs: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/dags" 
echo " Plugins: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/plugins"
echo " Логи: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/logs"
echo " БД: N/A (PostgreSQL)"
echo " Порт: 8082"
echo " Исполнитель: LocalExecutor"
echo ""
echo " Все пути сформированы программно и являются абсолютными!"
echo " Режим развертывания: PostgreSQL (порт 8082)"
