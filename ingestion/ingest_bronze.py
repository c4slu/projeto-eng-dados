
import os
from datetime import datetime
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Conexão com o MinIO (S3 local)
# Dentro do container: http://minio:9000  |  Na sua máquina: http://localhost:9000
# ---------------------------------------------------------------------------
STORAGE_OPTIONS = {
    "key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    "secret": os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
    "client_kwargs": {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    },
}

BRONZE_PATH = os.getenv("BRONZE_PATH", "s3://bronze/cripto/")

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1,
}


def main():
    print(f"Chamando a API da CoinGecko...")
    resposta = requests.get(API_URL, params=PARAMS, timeout=30)
    resposta.raise_for_status()  # quebra se a API retornar erro (4xx/5xx)

    dados = resposta.json()
    print(f"  -> {len(dados)} registros recebidos")

    # Converte o JSON cru direto para DataFrame (sem limpeza — isso é a bronze)
    df = pd.DataFrame(dados)

    # Particiona por data de extração (boa prática)
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    destino = f"{BRONZE_PATH}data={hoje}/dados.parquet"

    print(f"Gravando na camada bronze: {destino}")
    df.to_parquet(destino, storage_options=STORAGE_OPTIONS, index=False)
    print(f"  -> {len(df)} linhas gravadas com sucesso")


if __name__ == "__main__":
    main()