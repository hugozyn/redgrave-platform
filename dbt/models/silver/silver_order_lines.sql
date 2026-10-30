select
    i.order_id, i.line_no, o.order_date, o.channel, o.status,
    p.product_id, p.sku, p.category, i.qty, i.unit_price_gbp,
    i.qty * i.unit_price_gbp as line_revenue_gbp
from {{ source('bronze', 'order_items') }} i
join {{ ref('silver_orders') }} o on o.order_id = i.order_id
join {{ ref('silver_products') }} p on p.product_id = i.product_id
