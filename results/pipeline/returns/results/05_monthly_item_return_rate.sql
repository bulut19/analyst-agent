WITH base AS (
  SELECT
    DATE_TRUNC(DATE(oi.created_at), MONTH) AS order_month,
    CASE LOWER(TRIM(p.category))
      WHEN 'jeans' THEN 'Jeans'
      WHEN 'tops and tees' THEN 'Tops & Tees'
      WHEN 'sweater' THEN 'Sweaters'
      WHEN 'accesories' THEN 'Accessories'
      ELSE INITCAP(LOWER(TRIM(p.category)))
    END AS category,
    p.brand AS brand,
    oi.status AS status
  FROM `analyst-agent-512103.thelook_dirty.order_items` oi
  JOIN `analyst-agent-512103.thelook_dirty.products` p
    ON oi.product_id = p.id
  WHERE oi.created_at >= TIMESTAMP('2025-10-01')
    AND oi.created_at < TIMESTAMP('2026-10-01')
    AND oi.sale_price > 0
    AND oi.status IN ('Complete', 'Returned')
),
months AS (
  SELECT m AS order_month
  FROM UNNEST(GENERATE_DATE_ARRAY(DATE '2025-10-01', DATE '2026-09-01', INTERVAL 1 MONTH)) AS m
),
company_month AS (
  SELECT
    mo.order_month,
    COUNT(b.status) AS items_sold,
    COUNTIF(b.status = 'Returned') AS items_returned
  FROM months mo
  LEFT JOIN base b ON b.order_month = mo.order_month
  GROUP BY mo.order_month
),
company_total AS (
  SELECT SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS company_rate_12m
  FROM base
),
cat_sel AS (
  SELECT category AS dim_name
  FROM (
    SELECT
      category,
      COUNT(*) AS items_sold,
      SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS rate_12m
    FROM base
    WHERE category IS NOT NULL
    GROUP BY category
    HAVING COUNT(*) >= 100
  )
  CROSS JOIN company_total
  ORDER BY (rate_12m - company_rate_12m) DESC, category
  LIMIT 10
),
brand_sel AS (
  SELECT brand AS dim_name
  FROM (
    SELECT
      brand,
      COUNT(*) AS items_sold,
      SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*)) AS rate_12m
    FROM base
    WHERE brand IS NOT NULL
    GROUP BY brand
    HAVING COUNT(*) >= 100
  )
  CROSS JOIN company_total
  ORDER BY (rate_12m - company_rate_12m) DESC, brand
  LIMIT 15
),
cat_monthly AS (
  SELECT
    'Category' AS view_type,
    s.dim_name,
    mo.order_month,
    COUNT(b.status) AS items_sold,
    COUNTIF(b.status = 'Returned') AS items_returned
  FROM cat_sel s
  CROSS JOIN months mo
  LEFT JOIN base b ON b.category = s.dim_name AND b.order_month = mo.order_month
  GROUP BY s.dim_name, mo.order_month
),
brand_monthly AS (
  SELECT
    'Brand' AS view_type,
    s.dim_name,
    mo.order_month,
    COUNT(b.status) AS items_sold,
    COUNTIF(b.status = 'Returned') AS items_returned
  FROM brand_sel s
  CROSS JOIN months mo
  LEFT JOIN base b ON b.brand = s.dim_name AND b.order_month = mo.order_month
  GROUP BY s.dim_name, mo.order_month
),
company_rows AS (
  SELECT 'Company' AS view_type, 'Company' AS dim_name, order_month, items_sold, items_returned
  FROM company_month
),
all_rows AS (
  SELECT * FROM cat_monthly
  UNION ALL
  SELECT * FROM brand_monthly
  UNION ALL
  SELECT * FROM company_rows
)
SELECT
  a.order_month AS order_month,
  a.view_type AS view_type,
  a.dim_name AS category_or_brand,
  a.items_sold AS items_sold,
  a.items_returned AS items_returned,
  SAFE_DIVIDE(a.items_returned, a.items_sold) AS return_rate,
  SAFE_DIVIDE(cm.items_returned, cm.items_sold) AS company_return_rate,
  SAFE_DIVIDE(a.items_returned, a.items_sold) - SAFE_DIVIDE(cm.items_returned, cm.items_sold) AS gap_to_company_rate,
  a.order_month >= DATE '2026-08-01' AS is_immature_month
FROM all_rows a
JOIN company_month cm ON cm.order_month = a.order_month
ORDER BY
  CASE a.view_type WHEN 'Company' THEN 0 WHEN 'Category' THEN 1 ELSE 2 END,
  a.dim_name,
  a.order_month
