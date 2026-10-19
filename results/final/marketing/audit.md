# Data Quality Audit

Four problems could distort the repeat rate: future-dated orders, duplicate order IDs, orders with no customer, and the 400–999 item orders. Two date-order findings are real but only slightly affect this brief. The repeated emails and the Kagawa and Austria spellings are not errors. Two decisions are needed: how to treat the suspect orders, and whether one person with several accounts counts as one customer.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| high | `orders.created_at` | 5 | Five orders are dated 2027–2028, which is after the data ends (September 2026). They cannot be real. If kept, they could be counted as a customer's first or second order. That would wrongly make someone a repeat buyer, or move their first-order month. | Exclude orders with created_at later than the data cut-off (30 Sep 2026) from all calculations. Do not use them as first or second orders. Report the count excluded. |
| high | `orders.order_id` | 5 | Some order IDs appear more than once. A duplicated order can look like a second order from the same customer. That would count a one-time buyer as a repeat buyer. Duplicates also break joins to order items. | Check whether duplicate rows are exact copies. If they are, keep one row per order_id. If they conflict, keep the earliest-created row, or exclude the order_id if it can't be resolved. Count distinct order_id only. Count a repeat only when the second order has a different order_id and a different date or time. |
| medium | `orders.user_id` | 5 | Five orders have no customer attached, so they can't be linked to a marketing channel. They cannot count toward any customer's first or second order. Their effect is small, but a real repeat purchase could be missed. | Exclude orders where user_id is null from the customer-level KPIs. Report how many were excluded. |
| medium | `orders.num_of_item` | 5 | Five orders list 120 to 999 items, while 99% of orders have 4 or fewer. These look like entry errors or test orders. The brief counts orders rather than items, so the effect is limited. But if one of these is a customer's second order, it would wrongly make them a repeat buyer. | Treat orders with num_of_item > 40 as invalid. Exclude them from the first-order and second-order logic. Cross-check num_of_item against the count of rows in order_items. |
| low | `orders.created_at, delivered_at` | 5 | Five orders show delivery before the order was created, which is impossible. The brief uses order creation dates and status, not delivery dates. So it does not affect the KPIs directly. It does suggest those orders' other fields may be unreliable. | Don't use delivered_at in this dashboard. Flag these orders for review. Do not exclude them solely for this reason. |
| low | `orders.shipped_at, delivered_at` | 5 | Five orders show delivery before shipping. These are the same orders as in the delivery-before-creation finding. The brief does not use shipping or delivery dates, so the KPIs are not affected. | Don't use shipped_at or delivered_at. Flag these orders for review. Do not exclude them solely for this reason. |

## Decisions needed

- **orders.num_of_item:** Orders with more than 40 items look like errors. Can we exclude them from the repeat-rate calculation, or are some of them real bulk or wholesale orders?

## Flagged but not a problem

| Verdict | Table.column | Rows | Why |
|---|---|---|---|
| expected | `users.email` | 25,534 | About 25,000 rows share an email with another row. The check flags many rows, but each user has a unique id. In a synthetic or retail dataset, repeated emails are plausible. The brief counts customers by user id. The risk is that one person with several accounts could be counted as several new customers. Nothing in the data lets us merge accounts safely. |
| false alarm | `users.state` | 5 | Kagawa and Kanagawa are two different prefectures in Japan. This is not a misspelling. State is not used in the brief. |
| false alarm | `users.country` | 2 | Austria and Australia are two different countries. This is not a misspelling. Country is not used in the brief. |
