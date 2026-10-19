WITH base AS (
  SELECT
    CASE
      WHEN LOWER(REGEXP_REPLACE(TRIM(p.category), r'\s+', ' ')) = 'tops and tees' THEN 'Tops & Tees'
      WHEN LOWER(REGEXP_REPLACE(TRIM(p.category), r'\s+', ' ')) = 'sweater' THEN 'Sweaters'
      WHEN LOWER(REGEXP_REPLACE(TRIM(p.category), r'\s+', ' ')) = 'accesories' THEN 'Accessories'
      ELSE INITCAP(LOWER(REGEXP_REPLACE(TRIM(p.category), r'\s+', ' ')))
    END AS category,
    COALESCE(NULLIF(TRIM(p.brand), ''), 'Unknown') AS brand,
    oi.status AS status
  FROM `analyst-agent-512103.thelook_dirty.order_items` oi
  JOIN `analyst-agent-512103.thelook_dirty.products` p
    ON oi.product_id = p.id
  WHERE oi.created_at >= TIMESTAMP('2025-10-01')
    AND oi.created_at < TIMESTAMP('2026-10-01')
    AND oi.status IN ('Complete', 'Returned')
    AND oi.sale_price > 0
),
company AS (
  SELECT SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS company_return_rate
  FROM base
),
cat AS (
  SELECT
    'category' AS breakdown,
    category AS name,
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned
  FROM base
  GROUP BY category
  HAVING COUNT(*) >= 100
),
brd AS (
  SELECT
    'brand' AS breakdown,
    brand AS name,
    COUNT(*) AS items_sold,
    COUNTIF(status = 'Returned') AS items_returned
  FROM base
  WHERE brand != 'Unknown'
  GROUP BY brand
  HAVING COUNT(*) >= 100
),
brd_top AS (
  SELECT b.*
  FROM brd b CROSS JOIN company c
  ORDER BY ABS(SAFE_DIVIDE(b.items_returned, b.items_sold) - c.company_return_rate) DESC
  LIMIT 15
),
combined AS (
  SELECT * FROM cat
  UNION ALL
  SELECT * FROM brd_top
)
SELECT
  x.breakdown,
  x.name,
  x.items_sold,
  x.items_returned,
  SAFE_DIVIDE(x.items_returned, x.items_sold) AS return_rate,
  c.company_return_rate,
  SAFE_DIVIDE(x.items_returned, x.items_sold) - c.company_return_rate AS gap_to_company
FROM combined x CROSS JOIN company c
ORDER BY x.breakdown,
  ABS(SAFE_DIVIDE(x.items_returned, x.items_sold) - c.company_return_rate) DESC
