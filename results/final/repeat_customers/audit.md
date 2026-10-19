# Data Quality Audit

Four of the nine findings could distort the repeat rate. The worst are duplicate order IDs, orders with no customer, and orders dated in 2027–2028. The other issues are minor, and two are false alarms or expected (Kagawa/Kanagawa and Austria/Australia are real places, and shared emails don't matter here). Two items need a business decision: how to treat duplicate orders and orders dated in the future.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| high | `orders.created_at` | 5 | Five orders are dated 2027 or 2028, but the data only runs to September 2026. These dates are impossible. If kept, they could be treated as a customer's first or second order. That would create fake repeaters, or put customers in a first-order year that does not exist. The true order date is unknown, so they can't be fixed. | Exclude orders with created_at later than the last valid data date (end of September 2026) from first-order and second-order logic. Log them in an exceptions list. Do not try to guess the correct date. |
| medium | `orders.order_id` | 5 | Some order IDs appear more than once (5 rows affected). If these are the same order copied twice, a customer would look like they placed two orders. That would count them as a repeat customer by mistake. If they are two different orders sharing an ID, dropping one would lose a real order. | Check whether duplicate rows are identical (same user, date, status). If so, keep one row per order_id. If they differ, flag them and keep the earliest created_at row. Count distinct order_id when finding a customer's second order. |
| medium | `orders.user_id` | 5 | Five orders have no customer attached. They can't be linked to anyone, so they can't count as a first or second order. They are very few, but they could make a customer's second order go missing. | Exclude orders where user_id is null from all customer-level calculations. Report the count of excluded orders. |
| low | `orders.num_of_item` | 5 | Five orders show 120 to 999 items, which looks like bad data. The repeat rate counts orders, not items, so item counts don't change it. These orders may be part of the same bad rows as other findings, so a check is still worthwhile. | Do not filter on num_of_item for this dashboard. Flag these orders and check whether they overlap with other flagged orders (future dates, duplicates, missing customer). Exclude them only if they do. |
| low | `orders.created_at, delivered_at` | 5 | Five orders show delivery before the order was created. This is impossible, so the delivery date is wrong. The repeat rate uses the order creation date, not the delivery date, so the KPIs are not affected. | Do not use delivered_at in this dashboard. Keep these orders, since created_at looks valid. Flag the rows for the data owner. |
| low | `orders.shipped_at, delivered_at` | 5 | Five orders show delivery before shipping. Likely the same bad rows as finding 5. Shipping and delivery dates are not used in the repeat rate, so there is no impact. | none. Do not use shipped_at or delivered_at. Flag for the data owner. |

## Decisions needed

- **orders.created_at:** These 5 orders have dates in 2027–2028. We can't tell when they really happened. Is it OK to leave them out of the dashboard? It affects very few customers.

## Flagged but not a problem

| Verdict | Table.column | Rows | Why |
|---|---|---|---|
| expected | `users.email` | 25,534 | Many rows share an email. The customer ID, not email, identifies a customer. In this kind of data, shared emails are common. The dashboard should count customers by user ID. Do not merge customers by email, because that would change group sizes. |
| false alarm | `users.state` | 5 | Kagawa and Kanagawa are two different Japanese prefectures. This is not a typo. State is also not used, since location is shown by country. |
| false alarm | `users.country` | 2 | Austria and Australia are two different countries. Merging them would put Austrian customers in Australia and distort the country view. Keep them separate. |
