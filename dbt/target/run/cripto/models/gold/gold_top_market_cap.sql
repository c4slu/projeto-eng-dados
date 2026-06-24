
  
    

  create  table "warehouse"."public"."gold_top_market_cap__dbt_tmp"
  
  
    as
  
  (
    -- GOLD: Top 10 moedas por valor de mercado.

select
    market_cap_rank,
    name,
    symbol,
    current_price,
    market_cap,
    total_volume
from "warehouse"."public"."stg_cripto"
order by market_cap desc
limit 10
  );
  