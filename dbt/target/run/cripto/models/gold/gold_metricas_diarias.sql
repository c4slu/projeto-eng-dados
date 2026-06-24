
  
    

  create  table "warehouse"."public"."gold_metricas_diarias__dbt_tmp"
  
  
    as
  
  (
    -- GOLD: Métricas agregadas por dia de processamento.

select
    cast(data_processamento as date) as data,
    count(*)                         as qtd_moedas,
    sum(market_cap)                  as market_cap_total,
    avg(current_price)               as preco_medio,
    avg(price_change_percentage_24h) as variacao_media_24h
from "warehouse"."public"."stg_cripto"
group by cast(data_processamento as date)
order by data desc
  );
  