WITH capped AS (
  SELECT order_id, user_id, status, created_at
  FROM `analyst-agent-512103.thelook_dirty.orders`
  WHERE user_id IS NOT NULL
    AND created_at < TIMESTAMP('2026-10-01')
),
dedup AS (
  SELECT order_id, user_id, status, created_at
  FROM capped
  QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at ASC) = 1
),
valid AS (
  SELECT * FROM dedup WHERE status NOT IN ('Cancelled','Returned')
),
data_end AS (
  SELECT DATE(MAX(created_at)) AS max_order_date FROM valid
),
first_order AS (
  SELECT user_id, MIN(created_at) AS first_created_at
  FROM valid
  GROUP BY user_id
),
u AS (
  SELECT id, traffic_source
  FROM `analyst-agent-512103.thelook_dirty.users`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY created_at ASC) = 1
),
cohorts AS (
  SELECT
    f.user_id,
    DATE_TRUNC(DATE(f.first_created_at), MONTH) AS cohort_month,
    COALESCE(u.traffic_source, 'Unknown channel') AS sign_up_channel
  FROM first_order f
  LEFT JOIN u ON u.id = f.user_id
  WHERE f.first_created_at >= TIMESTAMP('2023-10-01')
    AND f.first_created_at < TIMESTAMP('2025-10-01')
)
SELECT
  c.sign_up_channel,
  c.cohort_month,
  COUNT(DISTINCT c.user_id) AS new_customers,
  IF(COUNT(DISTINCT c.user_id) < 30, 'small group, low confidence', 'ok') AS confidence_flag
FROM cohorts c
CROSS JOIN data_end d
WHERE DATE_ADD(LAST_DAY(c.cohort_month, MONTH), INTERVAL 12 MONTH) <= d.max_order_date
GROUP BY c.sign_up_channel, c.cohort_month
ORDER BY c.cohort_month, c.sign_up_channel
