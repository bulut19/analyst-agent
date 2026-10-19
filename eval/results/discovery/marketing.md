# marketing

**Business question:** Which marketing channels bring customers who place a second order within 12 months of their first?

# Data Mapping

| Item | Type | Columns | Logic |
|---|---|---|---|
| New customers (cohort size) | kpi | `orders.user_id`, `orders.order_id`, `orders.status`, `orders.created_at`, `users.id`, `users.traffic_source` | Use orders (one row per order). Keep orders with status NOT IN ('Cancelled','Returned'). For each user_id, find the earliest valid created_at across all history (not just the dashboard window). That is the customer's first valid order. Count distinct users per first-order month and per users.traffic_source. |
| Repeat customers | kpi | `orders.user_id`, `orders.order_id`, `orders.status`, `orders.created_at` | Using the same valid orders, count customers who have a later valid order on a calendar date after the date of their first valid order, and no later than 12 calendar months after it (DATE(created_at) > first date AND <= DATE_ADD(first date, INTERVAL 12 MONTH)). Different order_ids on the same date as the first order do not count. Count each customer once. |
| 12-month repeat purchase rate | kpi | `orders.user_id`, `orders.order_id`, `orders.status`, `orders.created_at`, `users.traffic_source` | Repeat customers divided by New customers (cohort size), for each channel and cohort month. For the 3-month or quarterly rolling view, add up repeat customers and cohort sizes across the months first, then divide. Do not average monthly rates. The all-channel average is the same ratio across all channels. |
| Marketing channel | dimension | `users.traffic_source` | Take users.traffic_source (Search, Organic, Facebook, Email, Display) via orders.user_id = users.id. It is one value per customer, recorded at sign-up. It is used as the channel for the customer's cohort. |
| Month of first order (cohort month) | dimension | `orders.created_at`, `orders.status`, `orders.user_id` | Cohort month = month (UTC) of the customer's earliest valid order's created_at, where valid means status not Cancelled or Returned. |
| Marketing channel (filter) | filter | `users.traffic_source` | Filter on the five traffic_source values. |
| Cohort month range (filter) | filter | `orders.created_at` | Filter on the first-valid-order month, applied after the first order is worked out per customer. Do not filter orders by date before finding each customer's first order. That would wrongly make returning customers look new. |
| Customer gender (optional filter) | filter | `users.gender` | Use users.gender (F or M) joined via orders.user_id = users.id. Do not use orders.gender or products.department. |
| Age band (optional filter) | filter | `users.age` | Build bands from users.age (12 to 70). The band edges need to be agreed, for example under 25, 25-34, 35-44, 45-54, 55+. Age is the current value on the customer record, not the age at first order. |
| Location (optional filter) | filter | `users.country`, `users.state`, `users.city` | Filter on users.country, with users.state and users.city as finer levels. Country is the sensible level. State and city have hundreds to thousands of values. |
| Time range: last 24 matured cohort months (Oct 2023 – Sep 2025) | time_range | `orders.created_at` | Keep cohorts whose first-valid-order month is between 2023-10-01 and 2025-09-30. A cohort is shown only if its last day plus 12 months is on or before the latest order date in the data (2026-09-30). Calculate this cut-off from MAX(orders.created_at) rather than hard-coding it, so new cohorts appear as they mature. |

## Joins

- `orders.user_id = users.id (adds traffic_source, gender, age and location to each order)`
- `orders (first valid order per user) joined to orders (later valid orders) on user_id, with later created_at date > first order date and within 12 months, to find repeat customers`
- `order_items is not needed for the main metrics. If an item-level definition of a valid order is chosen, use order_items.order_id = orders.order_id`

## Gaps

- **Channel of the first order:** The data holds only users.traffic_source, the channel at sign-up. It is one value per customer. It is not recorded per order. It may not be the channel that drove the first purchase, especially if a customer signed up long before buying. *Substitute:* Use users.traffic_source as the acquisition channel. Label it 'sign-up channel' on the dashboard.
- **Which channel drove the repeat order:** There is no channel on orders or order_items. *Substitute:* none
- **Spend, cost per customer, return on spend, budget view:** There is no marketing spend table. Product cost and retail price are not marketing cost. *Substitute:* none
- **Age band and location filters:** Both exist, but age bands are not defined, and age is the current age, not the age at first order. *Substitute:* Agree the band edges. Use country as the location level.
- **Cohorts after Sep 2025:** They do not have 12 months of follow-up, so they are excluded by design. *Substitute:* none

## Data notes

- Order status is the current status, not the status at the time of ordering. Returned and cancelled orders are dropped completely, whenever the return happened. A customer's first valid order, and so their cohort, can change as later returns arrive. Recent cohorts are the most exposed.
- Orders with status Shipped or Processing count as valid under the brief. They may still become Returned or Cancelled. Please confirm. The share of these is likely to be small for cohorts older than a few months.
- orders.status is per order. order_items.status is per item and items in one order can differ. The mapping uses orders.status. An order with one returned item and other kept items is counted by its order status. Please confirm this is acceptable, or choose an item-level rule such as 'valid if at least one item is not cancelled or returned'.
- The first valid order is found across all history since 2019. A customer with an earlier valid order before Oct 2023 belongs to an earlier cohort, so they are not a new customer in the window.
- Same-day rule: orders are separate rows with different order_id values. A second order placed on the same calendar date (UTC) as the first is not counted as a repeat. This is the rule from the brief and needs confirming.
- '12 months' is calendar months from the first order date, for example 15 Mar 2024 to 15 Mar 2025. Timestamps are in UTC.
- users.traffic_source is set at sign-up. Customers who signed up a long time before their first order are still assigned to that channel.
- The users table has 96,898 rows but ids go up to 100,000. Some orders may have a user_id with no matching customer. An inner join would drop them. Check how many, and report them as 'unknown channel' or exclude them and say so.
- users.country has inconsistent labels: both 'Spain' and 'España', and 'Brasil'. Clean or group them before using location as a filter.
- Customer name and email are personal data. They must not appear on the dashboard. They are not needed here.
- order_items.created_at goes to 2026-10-04 but orders.created_at stops at 2026-09-30. Returned, shipped and delivered dates also run into October 2026. Use orders.created_at, with a cut-off of 2026-09-30, for cohort and maturity logic.
- Small channel-month groups can give noisy rates. Always show cohort size next to the rate. Use the rolling 3-month or quarterly view, calculated as summed repeat customers divided by summed cohort size.

*Column check: All columns exist in the schema.*
