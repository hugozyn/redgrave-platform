select
    order_id,
    upper(trim(customer_ref)) as customer_ref,
    lower(trim(channel)) as channel,
    lower(trim(status)) as status,
    order_ts,
    to_date(order_ts) as order_date,
    updated_at
from {{ source('bronze', 'orders') }}
qualify row_number() over (partition by order_id order by _loaded_at desc, updated_at desc) = 1
