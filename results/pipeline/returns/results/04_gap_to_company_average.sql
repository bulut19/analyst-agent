WITH base AS (
  SELECT
    oi.id,
    oi.status,
    CASE
      WHEN LOWER(TRIM(p.category)) = 'jeans' THEN 'Jeans'
      WHEN LOWER(TRIM(p.category)) = 'tops and tees' THEN 'Tops & Tees'
      WHEN LOWER(TRIM(p.category)) = 'sweater' THEN 'Sweaters'
      WHEN LOWER(TRIM(p.category)) = 'accesories' THEN 'Accessories'
      ELSE INITCAP(TRIM(p.category))
    END AS category_clean,
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
  SELECT
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned,
    SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS return_rate
  FROM base
),
cat AS (
  SELECT
    'category' AS level,
    category_clean AS group_name,
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE category_clean IS NOT NULL AND category_clean != ''
  GROUP BY category_clean
  HAVING COUNT(*) >= 100
),
br AS (
  SELECT
    'brand' AS level,
    brand AS group_name,
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE brand IS NOT NULL
  GROUP BY brand
  HAVING COUNT(*) >= 100
),
grp AS (
  SELECT c.level, c.group_name, c.items_sold, c.items_returned,
         SAFE_DIVIDE(c.items_returned, c.items_sold) AS return_rate
  FROM cat c
  UNION ALL
  SELECT * FROM (
    SELECT b.level, b.group_name, b.items_sold, b.items_returned,
           SAFE_DIVIDE(b.items_returned, b.items_sold) AS return_rate
    FROM br b
    CROSS JOIN company co
    ORDER BY SAFE_DIVIDE(b.items_returned, b.items_sold) - co.return_rate DESC
    LIMIT 15
  )
),
final AS (
  SELECT g.level, g.group_name, g.items_sold, g.items_returned, g.return_rate,
         co.return_rate AS company_return_rate,
         g.return_rate - co.return_rate AS gap_to_company
  FROM grp g
  CROSS JOIN company co
  UNION ALL
  SELECT 'company', 'Company-wide', items_sold, items_returned, return_rate, return_rate, 0.0
  FROM company
)
SELECT level, group_name, items_sold, items_returned, return_rate, company_return_rate, gap_to_company
FROM final
ORDER BY CASE level WHEN 'category' THEN 1 WHEN 'brand' THEN 2 ELSE 3 END,
         gap_to_company DESC
