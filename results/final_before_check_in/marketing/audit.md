# Data Quality Audit

Four problems could distort the repeat rate. These are future-dated orders, duplicate order IDs, orders with no customer, and 999-item style orders. Date-order errors need a quick decision. Duplicate emails may mean duplicate customer accounts, and that needs a decision because it affects who counts as a repeat customer. The two spelling flags are false alarms, and neither field is used in this brief.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| high | `orders.created_at` | 5 | Five orders are dated in 2027-2028, which is after the data ends (Sept 2026). The dates are impossible. If one is a customer's first or second order, it puts the customer in the wrong month or counts a fake repeat. The true order date is unknown. | Exclude orders where created_at is later than the data cut-off (2026-09-30 / today). Do not count them as first or second completed orders. Report the excluded count on the dashboard. |
| high | `orders.order_id` | 5 | Some order IDs appear twice. A duplicated order can look like a second order and make a one-time buyer look like a repeat customer. This inflates the repeat rate directly. The duplicates may be exact copies or different orders sharing an ID. | Check whether the duplicate rows are identical. If they are, keep one row per order_id. If they differ, keep the earliest-created row and flag the rest. Count repeat purchases only on distinct order_id values. |
| medium | `orders.user_id` | 5 | Five orders have no customer attached. They cannot be tied to any customer or channel, so they cannot be a first or second order. Only five rows, so the effect is small. | Exclude orders where user_id is null from all KPIs. Report the excluded count. |
| medium | `users.email` | 25,534 | About 25,500 customer rows share an email with another row. If the same person has two accounts, their orders are split between accounts. That makes repeat buyers look like two new one-time customers and lowers the repeat rate. It could also place one person in two channels. But it may be a feature of synthetic data, where common names collide on example emails, and these may be different people. It cannot be told from the data alone. | Until confirmed, treat each user id as one customer. Do not merge by email. Show the number of customers sharing an email as a caveat. If the business confirms the same email means the same person, merge accounts and use the earliest completed order across them and the channel of the earliest account. |
| low | `orders.num_of_item` | 5 | Five orders show 120 to 999 items, which is far outside the normal range (99% of orders have 4 or fewer). They look like entry errors. The brief counts orders, not items, so the repeat rate is not affected by item counts. They only matter if the order is also a wrong repeat order, or if item counts are added later. | Do not use num_of_item in these KPIs. Keep the orders for counting, but flag orders where num_of_item > 40 and exclude them if item counts or revenue are added later. |
| low | `orders.shipped_at, delivered_at` | 5 | Five orders were delivered before they were shipped. This is impossible. The brief uses order created date and status, not shipping or delivery dates, so the KPIs are not affected. It does suggest these rows have other errors. | Do not use shipped_at or delivered_at in these KPIs. Flag rows where delivered_at < shipped_at. Do not exclude them from the KPIs unless their created_at or status is also invalid. |
| low | `orders.created_at, delivered_at` | 5 | Same five orders as the shipping check, delivered before they were created. The delivery date is wrong. The created date is what the brief uses, and it looks plausible for these orders, so the KPIs are barely affected. One of them (order 11949) has a created date in June 2026, which is within the data range. | Use created_at as the order date. Ignore delivered_at. Flag rows where delivered_at < created_at. |

## Decisions needed

- **users.email:** Does the same email address mean the same person? If it does, should we combine those accounts into one customer, even if they show different marketing channels?

## Flagged but not a problem

| Verdict | Table.column | Rows | Why |
|---|---|---|---|
| false alarm | `users.state` | 5 | Kagawa and Kanagawa are two different prefectures in Japan. Kagawa is a real place, not a typo. Location is not used in this brief either. |
| false alarm | `users.country` | 2 | Austria and Australia are two different countries. Both are valid values. Country is not used in this brief. |
