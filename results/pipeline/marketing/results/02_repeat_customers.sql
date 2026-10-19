WITH dedup AS (
  SELECT order_id, user_id, status, created_at
  FROM `analyst-agent-512103.thelook_dirty.orders`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at) = 1
),
clean AS (
  SELECT order_id, user_id, status, created_at, DATE(created_at) AS order_date
  FROM dedup
  WHERE user_id IS NOT NULL
    AND created_at < TIMESTAMP('2026-10-01')
),
valid AS (
  SELECT order_id, user_id, order_date
  FROM clean
  WHERE COALESCE(status, '') NOT IN ('Cancelled', 'Returned')
),
bounds AS (
  SELECT MAX(order_date) AS max_date FROM valid
),
first_orders AS (
  SELECT user_id, MIN(order_date) AS first_date
  FROM valid
  GROUP BY user_id
),
cohorts AS (
  SELECT f.user_id, f.first_date, DATE_TRUNC(f.first_date, MONTH) AS cohort_month
  FROM first_orders f
  CROSS JOIN bounds b
  WHERE f.first_date >= DATE '2023-10-01'
    AND f.first_date <= DATE '2025-09-30'
    AND DATE_ADD(LAST_DAY(DATE_TRUNC(f.first_date, MONTH)), INTERVAL 12 MONTH) <= b.max_date
),
cust AS (
  SELECT c.user_id, c.cohort_month,
         COUNT(DISTINCT v.order_id) > 0 AS has_repeat
  FROM cohorts c
  LEFT JOIN valid v
    ON v.user_id = c.user_id
   AND v.order_date > c.first_date
   AND v.order_date <= DATE_ADD(c.first_date, INTERVAL 12 MONTH)
  GROUP BY c.user_id, c.cohort_month
),
u AS (
  SELECT id, traffic_source
  FROM `analyst-agent-512103.thelook_dirty.users`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY created_at) = 1
)
SELECT
  COALESCE(u.traffic_source, 'Unknown channel') AS signup_channel,
  cu.cohort_month AS cohort_month,
  COUNT(*) AS cohort_size,
  COUNTIF(cu.has_repeat) AS repeat_customers,
  SAFE_DIVIDE(COUNTIF(cu.has_repeat), COUNT(*)) AS repeat_rate,
  IF(COUNT(*) < 30, 'small group, low confidence', 'ok') AS confidence_flag
FROM cust cu
LEFT JOIN u ON u.id = cu.user_id
GROUP BY signup_channel, cohort_month
ORDER BY cohort_month, signup_channel
