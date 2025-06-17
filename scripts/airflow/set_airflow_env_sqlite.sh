#!/bin/bash
# Автоматически сгенерированный скрипт с переменными окружения Airflow
# Все пути программно сформированы как абсолютные
# Режим развертывания: SQLite (порт 8081)

echo " Установка переменных окружения Airflow с абсолютными путями..."
echo " Режим: SQLite (порт 8081)"

# Экспорт переменных окружения
export AIRFLOW_HOME="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/dags"
export AIRFLOW__CORE__PLUGINS_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/plugins"
export AIRFLOW__LOGGING__BASE_LOG_FOLDER="/Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/logs"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:////Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/airflow/airflow.db"
export AIRFLOW__CORE__EXECUTOR="SequentialExecutor"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
export AIRFLOW__WEBSERVER__SECRET_KEY="dev_secret_key_for_sqlite"
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="8081"
export AIRFLOW__CORE__CHECK_SLAS="False"
export AIRFLOW__CORE__STORE_SERIALIZED_DAGS="True"
export AIRFLOW__CORE__STORE_DAG_CODE="True"
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG="True"
export AIRFLOW__WEBSERVER__WORKERS="1"
export AIRFLOW__WEBSERVER__WORKER_TIMEOUT="300"

echo " Переменные окружения установлены:"
echo " Проект: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow"
echo " AIRFLOW_HOME: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/airflow"
echo " DAGs: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/dags" 
echo " Plugins: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/plugins"
echo " Логи: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/logs"
echo " БД: /Users/yuriy.samorodov/Documents/МФТИ/Семестр 2/Data Engineering/Exam/ml-pipeline-project/scripts/airflow/airflow/airflow.db"
echo " Порт: 8081"
echo " Исполнитель: SequentialExecutor"
echo ""
echo " Все пути сформированы программно и являются абсолютными!"
echo " Режим развертывания: SQLite (порт 8081)"
