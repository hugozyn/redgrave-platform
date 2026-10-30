-- Gold: best-selling products by paid revenue. Already written: read it and run it.
select
    sku,
    category,
    sum(qty)                    as units_sold,
    sum(line_revenue_gbp)       as revenue_gbp,
    rank() over (order by sum(line_revenue_gbp) desc) as revenue_rank
from {{ ref('silver_order_lines') }}
where status = 'paid'
group by sku, category
