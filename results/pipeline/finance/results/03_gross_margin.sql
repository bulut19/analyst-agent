WITH kept AS (
  SELECT
    DATE_TRUNC(DATE(oi.created_at), QUARTER) AS quarter_start,
    p.department AS department,
    oi.sale_price AS sale_price,
    p.cost AS cost
  FROM `analyst-agent-512103.thelook_dirty.order_items` AS oi
  INNER JOIN `analyst-agent-512103.thelook_dirty.products` AS p
    ON oi.product_id = p.id
  WHERE oi.created_at >= TIMESTAMP('2019-01-01')
    AND oi.created_at < TIMESTAMP('2026-10-01')
    AND oi.status IN ('Complete', 'Shipped', 'Processing')
    AND oi.returned_at IS NULL
    AND oi.sale_price > 0
    AND p.department IN ('Men', 'Women')
),
combined AS (
  SELECT quarter_start, department, sale_price, cost FROM kept
  UNION ALL
  SELECT quarter_start, 'Both' AS department, sale_price, cost FROM kept
)
SELECT
  quarter_start,
  department,
  COUNT(*) AS items_sold,
  SUM(sale_price) AS revenue,
  SUM(sale_price - cost) AS gross_margin,
  SAFE_DIVIDE(SUM(sale_price - cost), NULLIF(SUM(sale_price), 0)) AS gross_margin_rate
FROM combined
GROUP BY quarter_start, department
ORDER BY quarter_start, CASE department WHEN 'Men' THEN 1 WHEN 'Women' THEN 2 ELSE 3 END
