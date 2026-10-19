WITH items AS (
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
by_dept AS (
  SELECT
    quarter_start,
    department,
    SUM(sale_price) AS revenue,
    SUM(sale_price - cost) AS gross_margin
  FROM items
  GROUP BY quarter_start, department
),
both_depts AS (
  SELECT
    quarter_start,
    'Both' AS department,
    SUM(revenue) AS revenue,
    SUM(gross_margin) AS gross_margin
  FROM by_dept
  GROUP BY quarter_start
),
all_rows AS (
  SELECT * FROM by_dept
  UNION ALL
  SELECT * FROM both_depts
)
SELECT
  cur.quarter_start AS quarter_start,
  CONCAT(CAST(EXTRACT(YEAR FROM cur.quarter_start) AS STRING), ' Q', CAST(EXTRACT(QUARTER FROM cur.quarter_start) AS STRING),
         IF(cur.quarter_start = DATE '2026-07-01', ' (to 30 Sep 2026)', '')) AS quarter_label,
  cur.department AS department,
  cur.revenue AS revenue,
  prev.revenue AS revenue_prior_year,
  SAFE_DIVIDE(cur.revenue - prev.revenue, prev.revenue) AS revenue_change_pct,
  cur.gross_margin AS gross_margin,
  prev.gross_margin AS gross_margin_prior_year,
  SAFE_DIVIDE(cur.gross_margin - prev.gross_margin, prev.gross_margin) AS gross_margin_change_pct,
  SAFE_DIVIDE(cur.gross_margin, cur.revenue) AS gross_margin_pct,
  SAFE_DIVIDE(prev.gross_margin, prev.revenue) AS gross_margin_pct_prior_year,
  SAFE_DIVIDE(cur.gross_margin, cur.revenue) - SAFE_DIVIDE(prev.gross_margin, prev.revenue) AS gross_margin_pct_point_change,
  IF(cur.quarter_start = DATE '2020-01-01', 'Prior quarter is partial - change is overstated', NULL) AS comparison_flag
FROM all_rows AS cur
LEFT JOIN all_rows AS prev
  ON prev.department = cur.department
  AND prev.quarter_start = DATE_SUB(cur.quarter_start, INTERVAL 1 YEAR)
WHERE cur.quarter_start >= DATE '2020-01-01'
ORDER BY cur.quarter_start,
  CASE cur.department WHEN 'Men' THEN 1 WHEN 'Women' THEN 2 ELSE 3 END
