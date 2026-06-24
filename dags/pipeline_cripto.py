"""
pipeline_cripto.py
------------------
Pipeline completo de ponta a ponta:

    ingestao_bronze -> transformacao_silver -> carga_warehouse -> dbt_run

As tres primeiras tasks rodam scripts Python dentro do proprio Airflow.
A ultima (dbt) sobe o container dbt via Docker e executa "dbt run".
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

default_args = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="pipeline_cripto",
    description="Pipeline cripto completo: bronze -> silver -> warehouse -> gold (dbt)",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
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

    carga_warehouse = BashOperator(
        task_id="carga_warehouse",
        bash_command="python /opt/airflow/warehouse/load_warehouse.py",
    )

    # Sobe o container dbt, roda "dbt run" e encerra.
    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="projeto-data-enginner-dbt",   # nome da imagem buildada pelo compose
        command="run",                        # vira "dbt run" (entrypoint = dbt)
        working_dir="/usr/app/dbt",
        environment={"DBT_PROFILES_DIR": "/usr/app/dbt"},
        mounts=[
            Mount(source="/c/www/projeto-data-enginner/dbt",
                  target="/usr/app/dbt", type="bind"),
        ],
        network_mode="projeto-data-enginner_data-net",  # mesma rede do postgres
        auto_remove="success",
        docker_url="unix://var/run/docker.sock",
        mount_tmp_dir=False,
    )

    ingestao_bronze >> transformacao_silver >> carga_warehouse >> dbt_run