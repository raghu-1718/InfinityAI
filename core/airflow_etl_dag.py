from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    print("Extracting data...")

def transform():
    print("Transforming data...")

def load():
    print("Loading data...")

def notify():
    print("ETL complete!")

default_args = {
    'owner': 'InfinityAI',
    'start_date': datetime(2025, 9, 13),
}

dag = DAG('infinityai_etl', default_args=default_args, schedule_interval='@daily')

extract_task = PythonOperator(task_id='extract', python_callable=extract, dag=dag)
transform_task = PythonOperator(task_id='transform', python_callable=transform, dag=dag)
load_task = PythonOperator(task_id='load', python_callable=load, dag=dag)
notify_task = PythonOperator(task_id='notify', python_callable=notify, dag=dag)

extract_task >> transform_task >> load_task >> notify_task
