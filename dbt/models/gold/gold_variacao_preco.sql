-- GOLD: Variação de preço em 24h (ordenado das maiores altas às maiores baixas).

select
    name,
    symbol,
    current_price,
    price_change_percentage_24h
from {{ ref('stg_cripto') }}
where price_change_percentage_24h is not null
order by price_change_percentage_24h desc