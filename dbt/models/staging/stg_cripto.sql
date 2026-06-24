-- Camada STAGING: seleciona e organiza as colunas relevantes da silver.
-- Vira uma VIEW no PostgreSQL (não duplica dados, sempre reflete a tabela base).

with origem as (
    select * from {{ source('raw', 'silver_cripto') }}
)

select
    id,
    symbol,
    name,
    current_price,
    market_cap,
    market_cap_rank,
    total_volume,
    price_change_percentage_24h,
    last_updated,
    data_processamento
from origem