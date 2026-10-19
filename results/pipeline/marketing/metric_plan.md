# Metric Plan

**Time window:** 2023-10-01 to 2025-09-30. Cohorts are customers whose first valid order was between 2023-10-01 and 2025-09-30 (24 monthly cohorts). Each cohort has a full 12 months of follow-up by 2026-09-30, the data end. Follow-up orders are counted up to 2026-09-30. The Sep 2025 cohort matures on 2026-09-30, so it is the last one shown. Cohorts after Sep 2025 are left out until they mature.

**Rules applied to every metric:**

- Orders source: orders table, one row per order. Use orders.created_at (UTC) for all dates. Do not use shipped_at, delivered_at or order_items dates.
- Valid order = orders.status NOT IN ('Cancelled','Returned'). Shipped, Processing and Complete count as valid. Status is the current status, not the status at order time. Order-level status is used, not item-level.
- Exclude orders with created_at later than 2026-09-30 (five orders dated 2027-2028). Do this before finding each customer's first and second order.
- Exclude orders with a null user_id (five orders). Report the excluded count on the dashboard.
- Count each order_id once. If duplicate rows are identical, keep one. If they differ, keep the row with the earliest created_at and flag the rest for review.
- Find each customer's first valid order across all history since 2019-01-13, before applying any cohort month filter. Never filter orders by date before this step. Otherwise returning customers would look new.
- Customer key = users.id (user_id). Duplicate-email accounts are not merged in the main view. A second view with accounts merged by shared email is reported alongside, until the stakeholder decides. Merging is only applied if rows sharing an email also match on name, age, gender and location.
- Channel = users.traffic_source (Search, Organic, Facebook, Email, Display), labelled 'Sign-up channel' on the dashboard. One value per customer. Orders whose user_id has no matching user row are shown as 'Unknown channel', not dropped silently, and their count is reported.
- Cohort month = calendar month (UTC) of the customer's first valid order date.
- Repeat = a different valid order_id whose calendar date (UTC) is after the first valid order's date and no later than 12 calendar months after it (for example 15 Mar 2024 to 15 Mar 2025). Orders on the same date as the first order do not count as repeats.
- Maturity rule: a cohort month is shown only if its last day plus 12 months is on or before the latest valid order date in the data (2026-09-30). Calculate this from MAX(orders.created_at) with the future-date rule applied, not hard-coded.
- Flag orders with num_of_item > 40. Keep them as orders if otherwise valid. Check none is a customer's only repeat order. Exclude them from any item or volume totals.
- Orders with delivery dates before created_at are kept, using created_at, and flagged for the data owner.
- No personal data (name, email) is shown. Results are aggregates only.
- Show cohort size next to every rate. Rates for channel-month groups with fewer than 30 new customers are marked 'small group, low confidence'.

## 1. New customers (cohort size)

*How many new customers did each channel bring in each month?*

- **Formula:** Count of distinct customers (user_id) whose first valid order date falls in the cohort month, grouped by sign-up channel. First valid order = earliest created_at among that customer's valid orders across all history.
- **Grain:** One row per sign-up channel per cohort month (5 channels + Unknown x 24 months, at most 144 rows).
- **Breakdowns:** Sign-up channel, Cohort month, Optional filters: gender, age band, country
- **Filters:** Cohort month between 2023-10 and 2025-09, matured cohorts only; Optional: channel, gender (users.gender F/M), age band (users.age, edges to be agreed), country (users.country, cleaned labels)
- **Time logic:** Placed in a period by the month of the customer's first valid order's created_at (UTC). Window: first orders from 2023-10-01 to 2025-09-30. Cut-off for maturity is 2026-09-30.
- **Cleaning:** Apply all shared rules.; Customers whose first valid order was before 2023-10-01 belong to an earlier cohort and are not counted.; Group country labels before using the location filter (Spain/España, Brasil/Brazil).
- **Excluded example:** A customer whose first valid order was in June 2022 and who ordered again in Nov 2023. They are not a new customer in Nov 2023.

## 2. Repeat customers

*How many customers in each cohort placed a second valid order within 12 months?*

- **Formula:** Count of distinct customers in the cohort who have at least one other valid order with order date > first valid order date and <= first valid order date + 12 calendar months. Each customer counted once.
- **Grain:** One row per sign-up channel per cohort month (at most 144 rows).
- **Breakdowns:** Sign-up channel, Cohort month, Optional filters: gender, age band, country
- **Filters:** Cohort month between 2023-10 and 2025-09, matured cohorts only; Optional: channel, gender, age band, country
- **Time logic:** Customer is placed in the cohort by the month of their first valid order. The repeat order must fall between the day after the first order date and the same day 12 months later (inclusive). Never beyond 2026-09-30.
- **Cleaning:** Apply all shared rules.; Count repeat on distinct order_id, so duplicated order rows cannot create a fake repeat.; A returned or cancelled second order does not count. If the first order was returned, the next valid order becomes the first order.
- **Excluded example:** A customer who placed two valid orders on the same day (different order_ids). The second order is not a repeat. Another: a customer whose second order was Returned.

## 3. 12-month repeat purchase rate

*Which channels bring customers who come back for a second order within 12 months?*

- **Formula:** Repeat customers divided by New customers (cohort size), for the same channel and cohort month. Shown as a percentage. For the quarterly or rolling 3-month view, sum repeat customers and sum cohort sizes across the months first, then divide. Never average monthly rates. The all-channel average is total repeat customers divided by total cohort size across all channels. Channel summary for the whole window is also sum divided by sum.
- **Grain:** One row per sign-up channel per cohort month (monthly view), plus one row per channel per rolling 3-month window and one all-channel row per month. Result is small enough to chart: 5-6 lines over 24 months.
- **Breakdowns:** Sign-up channel, Cohort month, Optional filters: gender, age band, country
- **Filters:** Cohort month between 2023-10 and 2025-09, matured cohorts only; Optional: channel, gender, age band, country
- **Time logic:** Placed in a period by the customer's first valid order month. 12-month follow-up window per customer: first order date + 1 day to first order date + 12 calendar months. Only cohorts fully matured by 2026-09-30.
- **Cleaning:** Apply all shared rules.; If cohort size is 0 for a channel-month, show blank, not 0%.; Mark groups with cohort size under 30 as low confidence.; Report a second version with accounts merged by shared email, next to the main version, until the duplicate-email question is settled.
- **Excluded example:** A customer whose first valid order was in October 2025. They do not have 12 months of history by 2026-09-30, so they are left out of the rate.

## Decisions assumed (please confirm)

- Duplicate emails (about 25,500 rows): keep each user_id as a separate customer in the main view. Also report the rate with accounts merged by shared email if they match on other details. The stakeholder can overrule.
- 'Last two years' = the 24 matured cohort months, Oct 2023 to Sep 2025, not the last 24 calendar months.
- A returned or cancelled first order means the customer is not a new customer in that month. Their first valid order sets the cohort instead. Their cohort can shift as later returns arrive.
- Sign-up channel (users.traffic_source) is used as the acquisition channel. It may differ from the channel of the first purchase. Label it 'Sign-up channel'.
- 12 months = 12 calendar months from the first order date, inclusive of the anniversary date.
- Same-day orders as the first order are not repeats. Only a valid order on a later date counts.
- Shipped and Processing orders count as valid, together with Complete. The stakeholder can overrule.
- Order-level status (orders.status) decides validity, not item-level status.
- Show a rolling 3-month view alongside monthly rates, computed as summed repeat customers over summed cohort size.
- Low-confidence flag threshold: fewer than 30 new customers in a channel-month group. The stakeholder can change the number.
- Orders with no matching user row show as 'Unknown channel' and the count is reported, not silently dropped.
- Orders with future dates (after 2026-09-30) and with null user_id are excluded, and counts reported.
- Optional filters (gender, age band, country) are offered but not confirmed. Suggested age bands: under 25, 25-34, 35-44, 45-54, 55+. Age is current age, not age at first order. Country is the only location level.
- Reader list is not confirmed. The dashboard is designed for marketing budget owners.
