"""
load_warehouse.py
-----------------
A "ponte" entre o data lake e o data warehouse.
Lê a camada SILVER (Parquet no MinIO) e grava numa tabela do PostgreSQL,
de onde o dbt vai transformar os dados na camada gold.
"""

import os
import pandas as pd
from sqlalchemy import create_engine

# ---- Conexão com o MinIO (data lake) ----
STORAGE_OPTIONS = {
    "key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    "secret": os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
    "client_kwargs": {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    },
}
SILVER_PATH = os.getenv("SILVER_PATH", "s3://silver/cripto/")

# ---- Conexão com o PostgreSQL (warehouse) ----
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_DB = os.getenv("PG_DB", "warehouse")
PG_USER = os.getenv("PG_USER", "airflow")
PG_PASS = os.getenv("PG_PASS", "airflow")

TABELA_DESTINO = "silver_cripto"


def main():
    print(f"Lendo a camada silver: {SILVER_PATH}")
    df = pd.read_parquet(SILVER_PATH, storage_options=STORAGE_OPTIONS)
    print(f"  -> {len(df)} linhas lidas")

    engine = create_engine(
        f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:5432/{PG_DB}"
    )

    print(f"Gravando na tabela '{TABELA_DESTINO}' do warehouse...")
    # if_exists="replace": recria a tabela a cada execução (full refresh, simples para estudo)
    df.to_sql(TABELA_DESTINO, engine, schema="public", if_exists="replace", index=False)
    print(f"  -> {len(df)} linhas gravadas no PostgreSQL com sucesso")


if __name__ == "__main__":
    main()
