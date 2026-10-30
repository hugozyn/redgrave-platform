select channel, count(distinct order_id) as paid_orders, sum(line_revenue_gbp) as revenue_gbp
from {{ ref('silver_order_lines') }}
where status = 'paid'
group by channel
