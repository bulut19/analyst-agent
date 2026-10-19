# Metric Plan

**Time window:** 2023-10-01 to 2025-09-30. This is the range for the cohort month, which is the month of a customer's first completed order. That gives 24 monthly cohorts. Repeat orders are followed up to 2026-09-30, the last day of data. The last cohort (first order on 2025-09-30) has its 12 months end on 2026-09-30, so every cohort has a full 12 months. Dates are in UTC.

**Rules applied to every metric:**

- Order table is orders, one row per order. order_items is not used.
- Only orders with orders.status = 'Complete' count. The value is 'Complete', not 'Completed'. Cancelled, Returned, Shipped and Processing are excluded as first orders and as repeat orders. Status is the current status, not its history.
- Clean the orders first, then find each customer's first completed order. Cleaning steps: (1) drop orders with created_at after 2026-09-30 23:59:59 UTC (five orders dated 2027-2028); (2) drop orders with a null user_id (five orders); (3) remove duplicate order_id rows: if the copies are identical keep one, if they differ keep the earliest-created row. Show the number of rows dropped by each step on the dashboard.
- Find each customer's first completed order over all history from 2019-01-13, not only inside the window. Only then filter on the cohort month. Customers whose first completed order was before 2023-10-01 are not new and are left out.
- Date column: orders.created_at (the date the order was placed), cut to the month in UTC. shipped_at, delivered_at and returned_at are never used. Their errors (delivered before shipped or created) do not affect these metrics.
- Cohort month = month of the customer's first completed order. The cohort is the set of customers whose cohort month falls from 2023-10 to 2025-09.
- A customer is a repeat customer if they have a different order_id, with status Complete, whose created_at is strictly later than the first completed order's created_at and no later than first created_at + 12 calendar months (timestamp to timestamp). A second order with the exact same timestamp as the first does not count.
- Channel = users.traffic_source on the customer record, shown as 'Signup channel'. It is one value per customer. Join orders.user_id = users.id as a left join from the cohort. Customers with no match in users are shown as 'Unknown'.
- Each user id is one customer. Accounts are not merged by email. The dashboard shows a caveat with the number of customers who share an email with another account.
- Do not use num_of_item. Do not use name or email fields. Customers are counted by id only.
- Rolled-up views (quarter, all months, all channels) add up counts first, then divide. Never average monthly rates.
- A row 'All channels' is added for each cohort month as the benchmark. It is built from pooled counts and includes customers with channel 'Unknown'.
- Cohort sizes are shown next to every rate. Cohorts with fewer than 30 customers are flagged 'small group' but not hidden.

## 1. 12-month repeat purchase rate

*Of the customers each channel brought in, what share placed a second completed order within 12 months of their first?*

- **Formula:** Numerator: number of distinct customers in the cohort who are repeat customers (a different Complete order, strictly later than their first Complete order and within first created_at + 12 calendar months). Denominator: number of distinct customers in the cohort (first Complete order in that month). Rate = numerator / denominator, shown as a percentage. Same rows as the other two metrics: rate = Repeat customers / New customers.
- **Grain:** One row per cohort month x channel. 24 months x (5 channels + 'Unknown' if present + 'All channels') rows. Columns: cohort_month, channel, new_customers, repeat_customers, repeat_rate.
- **Breakdowns:** Signup channel (Search, Organic, Facebook, Email, Display, Unknown) plus 'All channels' benchmark, Cohort month (2023-10 to 2025-09), Optional pooled view by quarter and a pooled 24-month total per channel (counts added, then divided)
- **Filters:** Cohort month between 2023-10 and 2025-09; Channel (filter by users.traffic_source); orders.status = 'Complete' for first and repeat orders
- **Time logic:** Cohort month comes from MIN(created_at) of the customer's cleaned Complete orders over all history, cut to the month in UTC. Cohort window: 2023-10-01 to 2025-09-30. A repeat order must have created_at after the first order and on or before first created_at + 12 calendar months, and not later than 2026-09-30.
- **Cleaning:** Apply all shared cleaning rules (future-dated orders, duplicate order_id, null user_id).; Count repeat orders on distinct order_id only, so a duplicated order cannot make a one-time buyer a repeat customer.; Latest cohorts may be slightly low because some recent Shipped or Processing orders may still become Complete. Show a note, with the count of recent orders in these statuses.
- **Excluded example:** A customer whose first Complete order was in March 2023 and who bought again in 2024 is not in any cohort. Also excluded: a customer whose only second order was Returned or Cancelled, which does not count as a repeat.

## 2. New customers (cohort size)

*How many customers did each channel bring in each month, so we can see which rates rest on small groups?*

- **Formula:** Count of distinct user_id whose first Complete order (earliest created_at among cleaned Complete orders over all history) falls in the cohort month. This is the denominator of the repeat rate.
- **Grain:** One row per cohort month x channel (including 'All channels'). Columns: cohort_month, channel, new_customers.
- **Breakdowns:** Signup channel plus 'All channels', Cohort month (2023-10 to 2025-09)
- **Filters:** Cohort month between 2023-10 and 2025-09; Channel
- **Time logic:** Placed in a month by the created_at of the customer's first Complete order, in UTC. Window: 2023-10-01 to 2025-09-30.
- **Cleaning:** Apply all shared cleaning rules.; A customer whose first order was Cancelled or Returned enters the cohort in the month of their first Complete order, if they have one. Customers with no Complete order are not counted.; Customers with no row in users are counted under 'Unknown'.
- **Excluded example:** A customer who only ever placed Cancelled or Returned orders has no completed order and is not counted. Also excluded: an order dated in 2027 that would otherwise be someone's first completed order.

## 3. Repeat customers

*How many customers in each channel and cohort month placed a second completed order within 12 months of their first?*

- **Formula:** Count of distinct user_id in the cohort who have at least one other Complete order (different order_id) with created_at strictly after their first Complete order and on or before first created_at + 12 calendar months. This is the numerator of the repeat rate. A customer is counted once, however many repeat orders they have.
- **Grain:** One row per cohort month x channel (including 'All channels'). Columns: cohort_month, channel, repeat_customers.
- **Breakdowns:** Signup channel plus 'All channels', Cohort month (2023-10 to 2025-09)
- **Filters:** Cohort month between 2023-10 and 2025-09; Channel
- **Time logic:** Customer is placed in a cohort month by the created_at of their first Complete order (UTC). The repeat order is found by created_at within 12 calendar months after the first, up to 2026-09-30.
- **Cleaning:** Apply all shared cleaning rules.; Use distinct order_id so duplicated orders do not create a fake second order.; A second order with the same timestamp as the first does not count.
- **Excluded example:** A customer with two items in a single Complete order has only one order, so they are not a repeat customer. A second Complete order placed 13 months after the first is also not counted.

## Decisions assumed (please confirm)

- Same email = same person? Recommended: No. Treat each user id as one customer and do not merge accounts. The dashboard shows how many customers share an email as a caveat. If you tell us the same email is the same person, we will merge accounts, use the earliest completed order across them and the channel of the earliest account.
- Window 'last 2 years': first orders from 2023-10-01 to 2025-09-30 (24 cohorts), the latest cohorts with a full 12 months of follow-up.
- 12-month rule: 12 calendar months from the first order's timestamp (first created_at + 12 months), not 365 days. Needs your sign-off.
- Second purchase: a different Complete order_id with a strictly later created_at than the first. Items in the same order do not count. Orders with the same timestamp do not count.
- Channel is the single signup channel stored on the customer record (users.traffic_source), labelled 'Signup channel'. It may not be the channel that led to the first purchase.
- Small groups: cohorts under 30 customers are flagged but still shown. A pooled quarterly view and a 24-month total per channel are offered, built from added-up counts. The threshold of 30 is our suggestion.
- Audience assumed to be the marketing lead or budget owner.
- Order status is the current status. Recent Shipped or Processing orders may still turn Complete, so the latest cohorts may be slightly understated.
- Future-dated orders (2027-2028), orders with no customer and duplicate order IDs are removed as per the audit's proposed rules. The removed counts are shown on the dashboard.
- Spend and value for money by channel cannot be shown. The data has no marketing spend. Organic is also not a paid channel.
