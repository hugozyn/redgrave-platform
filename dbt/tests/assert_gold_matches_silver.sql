-- Singular test: gold must not lose or invent revenue.
-- The test FAILS if this query returns a row.
select g.total_gold, s.total_silver
from (select sum(revenue_gbp) as total_gold from {{ ref('gold_revenue_by_channel') }}) g
cross join (
    select sum(line_revenue_gbp) as total_silver
    from {{ ref('silver_order_lines') }}
    where status = 'paid'
) s
where g.total_gold <> s.total_silver
