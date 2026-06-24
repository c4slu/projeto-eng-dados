-- GOLD: Top 10 moedas por valor de mercado.

select
    market_cap_rank,
    name,
    symbol,
    current_price,
    market_cap,
    total_volume
from {{ ref('stg_cripto') }}
order by market_cap desc
limit 10