WITH base AS (
  SELECT
    oi.status,
    INITCAP(CASE LOWER(TRIM(p.category))
      WHEN 'tops and tees' THEN 'tops & tees'
      WHEN 'sweater' THEN 'sweaters'
      WHEN 'accesories' THEN 'accessories'
      ELSE LOWER(TRIM(p.category))
    END) AS category,
    p.brand AS brand
  FROM `analyst-agent-512103.thelook_dirty.order_items` oi
  JOIN `analyst-agent-512103.thelook_dirty.products` p
    ON oi.product_id = p.id
  WHERE oi.created_at >= TIMESTAMP('2025-10-01')
    AND oi.created_at < TIMESTAMP('2026-10-01')
    AND oi.sale_price > 0
    AND oi.status IN ('Complete', 'Returned')
),
company AS (
  SELECT SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS company_return_rate
  FROM base
),
cat AS (
  SELECT 'category' AS breakdown_type, category AS breakdown_value,
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE category IS NOT NULL
  GROUP BY category
  HAVING COUNT(*) >= 100
),
br AS (
  SELECT 'brand' AS breakdown_type, brand AS breakdown_value,
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE brand IS NOT NULL
  GROUP BY brand
  HAVING COUNT(*) >= 100
),
cat_rates AS (
  SELECT c.*, SAFE_DIVIDE(items_returned, items_sold) AS return_rate,
    co.company_return_rate,
    SAFE_DIVIDE(items_returned, items_sold) - co.company_return_rate AS gap_to_company_rate
  FROM cat c CROSS JOIN company co
),
br_rates AS (
  SELECT b.*, SAFE_DIVIDE(items_returned, items_sold) AS return_rate,
    co.company_return_rate,
    SAFE_DIVIDE(items_returned, items_sold) - co.company_return_rate AS gap_to_company_rate
  FROM br b CROSS JOIN company co
),
br_top AS (
  SELECT * FROM br_rates
  ORDER BY gap_to_company_rate DESC
  LIMIT 15
)
SELECT * FROM cat_rates
UNION ALL
SELECT * FROM br_top
ORDER BY breakdown_type, gap_to_company_rate DESC
