-- GOLD: Métricas agregadas por dia de processamento.

select
    cast(data_processamento as date) as data,
    count(*)                         as qtd_moedas,
    sum(market_cap)                  as market_cap_total,
    avg(current_price)               as preco_medio,
    avg(price_change_percentage_24h) as variacao_media_24h
from {{ ref('stg_cripto') }}
group by cast(data_processamento as date)
order by data desc