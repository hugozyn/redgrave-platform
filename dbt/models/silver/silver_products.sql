-- Silver: clean product catalogue.
select
    product_id,
    upper(trim(sku))        as sku,
    trim(name)              as product_name,
    lower(trim(category))   as category,
    price_gbp
from {{ source('bronze', 'products') }}
