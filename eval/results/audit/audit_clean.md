# Data Quality Audit

Three real issues: duplicate customer emails, and shipped, delivered and returned dates that come before the order date. Duplicate emails could inflate customer counts. The date errors matter most for returns timing and delivery reporting. The two spelling findings are false alarms, because Kagawa and Austria are real places.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| medium | `users.email` | 25,534 | About 25,500 customer rows share an email with another row. The same person may have several customer records. If we count customer IDs, we overstate the number of customers and understate repeat buying. It could also be a sample-data artifact, where different people share a generated email. We need to confirm which. | Do not change the data yet. Check whether duplicate-email rows are the same person (same name, birth date, location) or different people. If same person, build a person key on normalised (lowercased, trimmed) email and count distinct person keys for customer metrics. If different people, keep customer ID as the key. |
| medium | `order_items.created_at, shipped_at` | 33,766 | About 33,800 order items show a ship date before the order was placed. That is impossible. Any average time-to-ship or time-to-deliver will be skewed, with negative values pulling the average down. Revenue totals are not affected because they do not use this date. | Exclude order items where shipped_at < created_at from time-to-ship calculations only. Keep them in revenue and order counts. Report the number excluded next to the metric. |
| medium | `order_items.created_at, delivered_at` | 5,761 | About 5,800 order items were delivered before they were ordered. That is impossible, so delivery-time averages would be wrong. Revenue is not affected. | Exclude order items where delivered_at < created_at (or delivered_at < shipped_at) from delivery-time calculations only. Keep them in revenue and order counts. |
| medium | `order_items.created_at, returned_at` | 637 | 637 items were returned before they were ordered. That is impossible. If returns are grouped by return date, they land in the wrong month, and days-to-return goes negative. The return flag itself is probably still valid, so return counts by order date are likely fine. | Keep these rows in return-rate counts, grouped by order date (created_at). Exclude rows where returned_at < created_at from days-to-return calculations. Do not group returns by returned_at until the dates are fixed. |

## Decisions needed

- **users.email:** Should one email address count as one customer, even if it has several customer IDs?
- **order_items.created_at, returned_at:** Should returns be reported by the month of the original order or by the month the item came back?

## Flagged but not a problem

| Verdict | Table.column | Rows | Why |
|---|---|---|---|
| false alarm | `users.state` | 5 | Kagawa and Kanagawa are two different prefectures in Japan. This is not a typo. |
| false alarm | `users.country` | 2 | Austria and Australia are two different countries. This is not a typo. |
