# Data Quality Audit

Four findings could change the repeat-rate numbers and need cleaning: duplicate order IDs, orders with no customer, orders dated in the future, and the 400–999 item orders. The date-order errors are low risk because the KPIs only use the order date. The duplicate emails look like a customer-identity problem and need a decision. The two spelling findings are false alarms, because the names are real and different.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| high | `users.email` | 25,534 | About 25,500 user rows share an email with another row. If one person has several user IDs, their orders are split across IDs. That makes real repeat buyers look like one-time buyers. It also counts one person as several new customers. The repeat rate would be too low and the cohort sizes too high. It could also be harmless: the sample emails are generic, and the data may be synthetic, so different people may share a name-based email. We cannot tell which without checking. | Do not merge or drop anything yet. First test whether rows sharing an email also share name, age, gender, location and signup details. If they do, treat them as one customer and use the earliest signup as the customer key. If they differ, keep user_id as the customer key and note the limit. Report the repeat rate both ways until it is settled. |
| high | `orders.created_at` | 5 | Five orders are dated 2027–2028, but the data ends in September 2026. These dates are impossible. If the customer's only other order is recent, a future-dated order could be counted as a repeat. Or it could be counted as a first order in a cohort that has not matured. Either way the numbers are distorted. | Exclude orders where created_at is later than the data cutoff (30 Sep 2026 / today). Apply this before working out each customer's first and second order. |
| medium | `orders.user_id` | 5 | Five orders have no customer. They cannot be linked to a customer or a channel. They cannot be counted as a first or second order. This is few rows, but if left in they could be counted wrongly or dropped without notice. | Exclude orders where user_id is null from all KPIs. Report the excluded count on the dashboard. |
| medium | `orders.order_id` | 5 | Five rows share an order ID (for example 15510 appears twice). A duplicated order could make a customer look like they ordered twice, and so look like a repeat buyer. Repeat counts would be too high. The brief says same-day orders count as one, which reduces the risk. But the duplicates may fall on different days. | Count each order_id once. If the duplicate rows are identical, keep one. If they differ, keep the earliest created_at and flag the others for review. Count repeat orders on distinct order_id. |
| low | `orders.num_of_item` | 5 | Five orders show 120 to 999 items, against a normal maximum of about 4. These are almost certainly entry errors. The KPIs count orders and customers, not items. So they will not change the rates, unless these orders are the only second order for a customer. Their validity is uncertain, so treat them with caution. | Flag orders with num_of_item > 40. Keep them in the repeat KPIs only if they are otherwise valid, and exclude them from any item or volume totals. Confirm that none is the sole second order of a customer. |
| low | `orders.shipped_at, delivered_at` | 5 | Five orders show delivery before shipping. The dates are wrong, but the KPIs use only the order created date and status. Delivery dates are not used. The impact is minimal. | No exclusion for the repeat KPIs. Do not use shipped_at or delivered_at in this dashboard. Flag the rows for the data owner. |
| low | `orders.created_at, delivered_at` | 5 | Five orders show delivery before the order was created. It is the same rows as the shipping-date problem. Created_at may be correct and delivered_at wrong, or the reverse. The dashboard needs created_at, so this raises a small doubt about those five order dates. | Keep these orders using created_at. Flag them for the data owner. Exclude them only if it is confirmed that created_at is the wrong field. |

## Decisions needed

- **users.email:** Should two accounts with the same email count as the same customer? If so, their orders would be combined and the earliest first order used. Or is each account a separate customer?

## Flagged but not a problem

| Verdict | Table.column | Rows | Why |
|---|---|---|---|
| false alarm | `users.state` | 5 | Kagawa and Kanagawa are two different prefectures in Japan. They are not a typo. Location is only an optional filter anyway. |
| false alarm | `users.country` | 2 | Austria and Australia are two different countries. This is not a misspelling. |
