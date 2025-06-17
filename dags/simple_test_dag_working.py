"""
Простой тестовый DAG для проверки работы Airflow.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Простая функция для тестирования
def test_function():
print("Тестовая функция работает!")
return "success"

# Определение DAG
default_args = {
'owner': 'admin',
'depends_on_past': False,
'start_date': datetime(2025, 6, 17),
'email_on_failure': False,
'email_on_retry': False,
'retries': 1,
'retry_delay': timedelta(minutes=5)
}

dag = DAG(
'test_simple_dag',
default_args=default_args,
description='Простой тестовый DAG',
schedule_interval=None,
catchup=False,
tags=['test', 'simple']
)

# Задача 1: Bash команда
bash_task = BashOperator(
task_id='print_date',
bash_command='date',
dag=dag
)

# Задача 2: Python функция
python_task = PythonOperator(
task_id='test_python',
python_callable=test_function,
dag=dag
)

# Определяем зависимости
bash_task >> python_task
