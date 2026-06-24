"""
pipeline_cripto.py
------------------
DAG do Airflow que orquestra o pipeline de criptomoedas:

    ingestao_bronze  ->  transformacao_silver

Cada etapa só roda depois que a anterior terminar com sucesso.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-eng",
    "retries": 1,                      # tenta de novo 1 vez se falhar
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="pipeline_cripto",
    description="Ingestao (bronze) e transformacao (silver) de dados de cripto",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",                 # roda uma vez por dia
    catchup=False,                     # nao executa datas passadas acumuladas
    tags=["estudo", "cripto"],
) as dag:

    ingestao_bronze = BashOperator(
        task_id="ingestao_bronze",
        bash_command="python /opt/airflow/ingestion/ingest_bronze.py",
    )

    transformacao_silver = BashOperator(
        task_id="transformacao_silver",
        bash_command="python /opt/airflow/spark/transform_silver.py",
    )

    # Define a ordem: silver só roda depois do bronze terminar
    ingestao_bronze >> transformacao_silver