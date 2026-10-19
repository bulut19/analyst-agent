WITH base AS (
  SELECT
    oi.id,
    oi.status,
    p.brand,
    INITCAP(TRIM(CASE LOWER(TRIM(p.category))
      WHEN 'tops and tees' THEN 'Tops & Tees'
      WHEN 'sweater' THEN 'Sweaters'
      WHEN 'accesories' THEN 'Accessories'
      ELSE p.category END)) AS category_clean
  FROM `analyst-agent-512103.thelook_dirty.order_items` oi
  JOIN `analyst-agent-512103.thelook_dirty.products` p
    ON oi.product_id = p.id
  WHERE oi.created_at >= TIMESTAMP('2025-10-01')
    AND oi.created_at < TIMESTAMP('2026-10-01')
    AND oi.sale_price > 0
    AND oi.status IN ('Complete','Returned')
),
company AS (
  SELECT SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS company_return_rate
  FROM base
),
cat AS (
  SELECT 'category' AS dimension_type, category_clean AS dimension_value,
         COUNT(*) AS items_sold,
         COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE category_clean IS NOT NULL
  GROUP BY category_clean
  HAVING COUNT(*) >= 100
),
br AS (
  SELECT 'brand' AS dimension_type, brand AS dimension_value,
         COUNT(*) AS items_sold,
         COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE brand IS NOT NULL
  GROUP BY brand
  HAVING COUNT(*) >= 100
),
combined AS (
  SELECT * FROM cat
  UNION ALL
  SELECT * FROM br
),
scored AS (
  SELECT c.dimension_type, c.dimension_value, c.items_sold, c.items_returned,
         SAFE_DIVIDE(c.items_returned, c.items_sold) AS return_rate,
         co.company_return_rate,
         SAFE_DIVIDE(c.items_returned, c.items_sold) - co.company_return_rate AS gap_to_company_rate
  FROM combined c
  CROSS JOIN company co
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY dimension_type ORDER BY gap_to_company_rate DESC, items_sold DESC) AS rn
  FROM scored
)
SELECT dimension_type, dimension_value, items_sold, items_returned, return_rate, company_return_rate, gap_to_company_rate
FROM ranked
WHERE dimension_type = 'category' OR rn <= 15
ORDER BY dimension_type, IF(dimension_type = 'brand', gap_to_company_rate, CAST(items_sold AS FLOAT64)) DESC
