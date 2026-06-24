# Imagem do dbt com o adaptador para PostgreSQL
FROM python:3.11-slim

# Instala o dbt-postgres (pode fixar uma versão depois, ex: dbt-postgres==1.8.9)
RUN pip install --no-cache-dir dbt-postgres

WORKDIR /usr/app/dbt

# Faz com que "docker compose run --rm dbt <comando>" execute "dbt <comando>"
ENTRYPOINT ["dbt"]
