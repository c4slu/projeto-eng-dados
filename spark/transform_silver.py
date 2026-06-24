"""
transform_silver.py
--------------------
Lê os dados crus da camada BRONZE no MinIO, faz uma limpeza simples
e grava o resultado tratado na camada SILVER.

Roda tanto DENTRO do container (Airflow) quanto na sua máquina:
o endereço do MinIO é lido de variável de ambiente, com padrão para cada caso.
"""

import os
import json
from datetime import datetime
import pandas as pd

# ---------------------------------------------------------------------------
# Conexão com o MinIO (S3 local)
# Dentro do container use http://minio:9000  |  Na sua máquina use http://localhost:9000
# ---------------------------------------------------------------------------
STORAGE_OPTIONS = {
    "key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    "secret": os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
    "client_kwargs": {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    },
}

# Ajuste os caminhos conforme você organizou o bronze na ingestão
BRONZE_PATH = os.getenv("BRONZE_PATH", "s3://bronze/cripto/")
SILVER_PATH = os.getenv("SILVER_PATH", "s3://silver/cripto/")


def main():
    print(f"Lendo dados da camada bronze: {BRONZE_PATH}")
    # Lê todos os arquivos parquet sob o prefixo bronze
    df = pd.read_parquet(BRONZE_PATH, storage_options=STORAGE_OPTIONS)
    print(f"  -> {len(df)} linhas lidas")

    # -------------------- LIMPEZA SIMPLES --------------------
    # 1) Padroniza nomes de colunas (minúsculo, sem espaços)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # 2) Achata colunas aninhadas (dict/list) convertendo para texto JSON.
    #    Sem isso, colunas como "roi" quebram operações como drop_duplicates.
    for col in df.columns:
        tem_aninhado = any(isinstance(x, (dict, list)) for x in df[col])
        if tem_aninhado:
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )
            print(f"  -> coluna aninhada achatada: {col}")

    # 3) Remove linhas totalmente duplicadas
    antes = len(df)
    df = df.drop_duplicates()
    print(f"  -> {antes - len(df)} duplicatas removidas")

    # 3) Remove linhas completamente vazias
    df = df.dropna(how="all")

    # 4) Adiciona metadado de processamento (boa prática)
    df["data_processamento"] = datetime.utcnow()
    # ---------------------------------------------------------

    # Particiona a saída por data, igual fizemos no bronze
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    destino = f"{SILVER_PATH}data={hoje}/dados.parquet"

    print(f"Gravando na camada silver: {destino}")
    df.to_parquet(destino, storage_options=STORAGE_OPTIONS, index=False)
    print(f"  -> {len(df)} linhas gravadas com sucesso")


if __name__ == "__main__":
    main()