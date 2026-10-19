WITH orders_dedup AS (
  SELECT order_id, user_id, status, created_at
  FROM `analyst-agent-512103.thelook_dirty.orders`
  WHERE user_id IS NOT NULL
    AND created_at < TIMESTAMP('2026-10-01')
  QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at ASC) = 1
),
valid AS (
  SELECT order_id, user_id, created_at, DATE(created_at) AS order_date
  FROM orders_dedup
  WHERE status NOT IN ('Cancelled', 'Returned')
),
max_date AS (
  SELECT MAX(order_date) AS d FROM valid
),
users_dedup AS (
  SELECT id, email, first_name, last_name, age, gender, state, city, country, traffic_source
  FROM `analyst-agent-512103.thelook_dirty.users`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY created_at ASC) = 1
),
users_keyed AS (
  SELECT id, traffic_source,
    IF(email IS NULL OR TRIM(email) = '', id,
       MIN(id) OVER (PARTITION BY LOWER(TRIM(email)), LOWER(TRIM(first_name)), LOWER(TRIM(last_name)), age, gender, state, city, country)) AS merge_key
  FROM users_dedup
),
v_keyed AS (
  SELECT v.order_id, v.user_id, v.created_at, v.order_date,
    COALESCE(u.traffic_source, 'Unknown channel') AS channel,
    COALESCE(u.merge_key, v.user_id) AS merge_key
  FROM valid v
  LEFT JOIN users_keyed u ON v.user_id = u.id
),
keyed AS (
  SELECT 'main' AS version, user_id AS cust_key, channel, order_id, created_at, order_date FROM v_keyed
  UNION ALL
  SELECT 'merged', merge_key, channel, order_id, created_at, order_date FROM v_keyed
),
firsts AS (
  SELECT version, cust_key, channel, order_id AS first_order_id, order_date AS first_date,
         DATE_TRUNC(order_date, MONTH) AS cohort_month
  FROM keyed
  QUALIFY ROW_NUMBER() OVER (PARTITION BY version, cust_key ORDER BY created_at ASC, order_id ASC) = 1
),
firsts_in_window AS (
  SELECT * FROM firsts
  WHERE first_date >= DATE '2023-10-01'
    AND first_date <= DATE '2025-09-30'
    AND DATE_ADD(LAST_DAY(first_date, MONTH), INTERVAL 12 MONTH) <= (SELECT d FROM max_date)
),
cust AS (
  SELECT f.version, f.cust_key, f.channel, f.cohort_month,
         LOGICAL_OR(k.order_id IS NOT NULL) AS is_repeat
  FROM firsts_in_window f
  LEFT JOIN keyed k
    ON k.version = f.version
   AND k.cust_key = f.cust_key
   AND k.order_id <> f.first_order_id
   AND k.order_date > f.first_date
   AND k.order_date <= DATE_ADD(f.first_date, INTERVAL 12 MONTH)
  GROUP BY 1, 2, 3, 4
),
agg AS (
  SELECT channel, cohort_month,
    COUNTIF(version = 'main') AS size_main,
    COUNTIF(version = 'main' AND is_repeat) AS rep_main,
    COUNTIF(version = 'merged') AS size_merged,
    COUNTIF(version = 'merged' AND is_repeat) AS rep_merged
  FROM cust
  GROUP BY 1, 2
),
months AS (
  SELECT m AS cohort_month
  FROM UNNEST(GENERATE_DATE_ARRAY(DATE '2023-10-01', DATE '2025-09-01', INTERVAL 1 MONTH)) AS m
  WHERE DATE_ADD(LAST_DAY(m, MONTH), INTERVAL 12 MONTH) <= (SELECT d FROM max_date)
),
channels AS (
  SELECT c AS channel FROM UNNEST(['Search', 'Organic', 'Facebook', 'Email', 'Display']) AS c
  UNION DISTINCT
  SELECT channel FROM agg
),
grid AS (
  SELECT ch.channel, mo.cohort_month,
    COALESCE(a.size_main, 0) AS size_main, COALESCE(a.rep_main, 0) AS rep_main,
    COALESCE(a.size_merged, 0) AS size_merged, COALESCE(a.rep_merged, 0) AS rep_merged
  FROM channels ch
  CROSS JOIN months mo
  LEFT JOIN agg a ON a.channel = ch.channel AND a.cohort_month = mo.cohort_month
),
base AS (
  SELECT * FROM grid
  UNION ALL
  SELECT 'All channels', cohort_month, SUM(size_main), SUM(rep_main), SUM(size_merged), SUM(rep_merged)
  FROM grid GROUP BY cohort_month
),
rolled AS (
  SELECT channel, cohort_month,
    MIN(cohort_month) OVER w AS window_start,
    COUNT(*) OVER w AS months_in_window,
    SUM(size_main) OVER w AS size_main, SUM(rep_main) OVER w AS rep_main,
    SUM(size_merged) OVER w AS size_merged, SUM(rep_merged) OVER w AS rep_merged
  FROM base
  WINDOW w AS (PARTITION BY channel ORDER BY cohort_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
),
combined AS (
  SELECT 'monthly' AS view_type, 1 AS view_order, channel, cohort_month AS window_start_month, cohort_month AS cohort_month,
         size_main, rep_main, size_merged, rep_merged
  FROM base
  UNION ALL
  SELECT 'rolling_3_month', 2, channel, window_start, cohort_month, size_main, rep_main, size_merged, rep_merged
  FROM rolled WHERE months_in_window = 3
  UNION ALL
  SELECT 'whole_window_total', 3, channel, MIN(cohort_month), CAST(NULL AS DATE),
         SUM(size_main), SUM(rep_main), SUM(size_merged), SUM(rep_merged)
  FROM base GROUP BY channel
)
SELECT
  view_type,
  channel AS sign_up_channel,
  window_start_month,
  cohort_month,
  size_main AS cohort_size,
  rep_main AS repeat_customers,
  SAFE_DIVIDE(rep_main, size_main) AS repeat_rate,
  CASE WHEN size_main = 0 THEN 'no new customers'
       WHEN size_main < 30 THEN 'small group, low confidence'
       ELSE '' END AS confidence_note,
  size_merged AS cohort_size_merged_accounts,
  rep_merged AS repeat_customers_merged_accounts,
  SAFE_DIVIDE(rep_merged, size_merged) AS repeat_rate_merged_accounts,
  CASE WHEN size_merged = 0 THEN 'no new customers'
       WHEN size_merged < 30 THEN 'small group, low confidence'
       ELSE '' END AS confidence_note_merged_accounts
FROM combined
ORDER BY view_order, cohort_month, sign_up_channel
