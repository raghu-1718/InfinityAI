# Airflow DAG for ETL pipeline
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

# Example ETL function

def extract():
    # Simulate data extraction
    data = pd.DataFrame({'symbol': ['AAPL', 'GOOG'], 'price': [150, 2800]})
    data.to_csv('/tmp/extracted.csv', index=False)

def transform():
    data = pd.read_csv('/tmp/extracted.csv')
    data['price'] = data['price'] * 1.01  # Simulate transformation
    data.to_csv('/tmp/transformed.csv', index=False)

def load():
    data = pd.read_csv('/tmp/transformed.csv')
    # Simulate loading to Delta Lake (or any data lake)
    data.to_parquet('/tmp/final.parquet')

def version_data():
    # Simulate data versioning
    import shutil, time
    ts = int(time.time())
    shutil.copy('/tmp/final.parquet', f'/tmp/final_{ts}.parquet')

default_args = {
    'owner': 'infinityai',
    'depends_on_past': False,
    'start_date': datetime(2025, 9, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('infinityai_etl', default_args=default_args, schedule_interval='@daily')

extract_task = PythonOperator(task_id='extract', python_callable=extract, dag=dag)
transform_task = PythonOperator(task_id='transform', python_callable=transform, dag=dag)
load_task = PythonOperator(task_id='load', python_callable=load, dag=dag)
version_task = PythonOperator(task_id='version_data', python_callable=version_data, dag=dag)

extract_task >> transform_task >> load_task >> version_task
