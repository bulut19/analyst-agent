WITH kept AS (
  SELECT
    DATE_TRUNC(DATE(oi.created_at, 'UTC'), QUARTER) AS quarter_start,
    p.department AS department,
    oi.sale_price AS sale_price
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
agg AS (
  SELECT quarter_start, department, SUM(sale_price) AS revenue
  FROM kept
  GROUP BY quarter_start, department
  UNION ALL
  SELECT quarter_start, 'Both' AS department, SUM(sale_price) AS revenue
  FROM kept
  GROUP BY quarter_start
),
quarters AS (
  SELECT q AS quarter_start
  FROM UNNEST(GENERATE_DATE_ARRAY(DATE '2019-01-01', DATE '2026-07-01', INTERVAL 1 QUARTER)) AS q
),
depts AS (
  SELECT 'Men' AS department, 1 AS dept_order
  UNION ALL SELECT 'Women', 2
  UNION ALL SELECT 'Both', 3
)
SELECT
  qt.quarter_start AS quarter_start,
  CASE
    WHEN qt.quarter_start = DATE '2026-07-01' THEN 'Q3 2026, to 30 Sep 2026'
    WHEN qt.quarter_start = DATE '2019-01-01' THEN 'Q1 2019, from 13 Jan 2019'
    ELSE CONCAT('Q', CAST(EXTRACT(QUARTER FROM qt.quarter_start) AS STRING), ' ', CAST(EXTRACT(YEAR FROM qt.quarter_start) AS STRING))
  END AS quarter_label,
  d.department AS department,
  ROUND(a.revenue, 2) AS revenue
FROM quarters AS qt
CROSS JOIN depts AS d
LEFT JOIN agg AS a
  ON a.quarter_start = qt.quarter_start AND a.department = d.department
ORDER BY qt.quarter_start, d.dept_order
