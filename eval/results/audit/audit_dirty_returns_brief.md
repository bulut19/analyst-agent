# Data Quality Audit

Most of the serious problems are in the product and item tables. Orphan product IDs, mixed-up category spellings, and bad return dates can all shift category or brand return rates. Several findings don't touch these KPIs, and three are not errors at all: the duplicate emails, Kagawa and Austria.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| high | `order_items.product_id` | 5 | Five order items point to product IDs (30001–30005) that do not exist in the products table. They have no category or brand. They would drop out of every category and brand view, or show up as a blank group. They would still count in the company-wide rate, so the gap to company average would be slightly off. | Exclude order items whose product_id is not in products.id from category and brand views. Apply the same exclusion to the company-wide rate so the comparison uses the same items. Report the excluded count. |
| medium | `products.category` | 5 | The same category appears under different spellings, such as 'JEANS', 'jeans ' and 'Jeans', or 'Sweater' and 'Sweaters'. Only five products are affected, but they would show as separate tiny categories. They would also be missing from the real category totals. Small categories would then fail the 100-item minimum. | Trim spaces and map to the standard names: JEANS and 'jeans ' -> Jeans; 'Tops and Tees' -> 'Tops & Tees'; Sweater -> Sweaters; Accesories -> Accessories. Check the brand column for the same problem. |
| medium | `order_items.created_at, returned_at` | 637 | 637 items have a return date before the order date. That is impossible. The 'returned' status is probably right, but the dates are unreliable. The brief places items in a month by order date, so the count may be fine. If the return date were used, the monthly trend could shift. Some of these gaps are only a few hours. They may be time-of-day or timezone noise rather than real errors. | Keep these items as returned and place them in a month by created_at. Do not use returned_at for month placement. Flag items where returned_at is more than 1 day before created_at as suspect, and exclude those if the stakeholder prefers. |
| low | `orders.num_of_item` | 5 | Five orders show 120–999 items, far above the normal maximum of about 4. These look like entry errors. The KPIs count rows in order_items, not the num_of_item field on orders, so the return rates are not directly affected. They would distort any measure that uses num_of_item. | Do not use orders.num_of_item. Count items from order_items rows. Exclude orders with num_of_item > 40 from any order-level figure. |
| low | `orders.created_at` | 5 | Five orders are dated in 2027–2028, which is in the future. They fall outside the 12-month window, so they will not be counted anyway. The dates are wrong, though, and the true order date is unknown. If their items carry status delivered or returned, they would be misplaced. | Exclude orders and their items with created_at later than the end of the latest complete month (August 2026). Log the five orders. |
| low | `order_items.sale_price` | 5 | Five items have a price of zero or less. A negative price is not a real sale, and a zero price may be a free or test item. The KPIs count items, not money. If these items are delivered or returned, they add a few wrong rows to the counts. | Exclude order items with sale_price <= 0 from all counts. |
| low | `orders.shipped_at, delivered_at` | 5 | Five orders were delivered before they were shipped. The dates are wrong, but the brief does not use order-level delivery or shipping dates. Item status decides what counts. | No exclusion needed. Do not use orders.shipped_at or delivered_at for month placement. Use created_at. |
| low | `orders.created_at, delivered_at` | 5 | The same five orders were delivered before they were created. Their dates are impossible. The KPIs do not use these dates, so there is no direct effect. | No exclusion needed. Use created_at for month placement. Optionally flag these orders as suspect. |
| low | `orders.order_id` | 5 | Five order rows repeat an order ID. If orders are joined to items, items could be counted twice. That would inflate sold and returned counts for a few items. | Count items from order_items by item id. When joining to orders, keep one row per order_id, using the earliest created_at. Check that item ids are unique. |
| none | `orders.user_id` | 5 | Five orders have no customer. The brief has no customer dimension or customer filter, so return rates by category and brand are unaffected. | none |

## Decisions needed

- **order_items.created_at, returned_at:** Should items with an impossible return date still count as returned? We suggest yes, placed by order date. Or should we drop them?
- **order_items.sale_price:** Should zero-price items be treated as real sales, such as free gifts, or removed? We suggest removing the negative ones and checking the zero ones.

## Flagged but not a problem

| Verdict | Table.column | Rows | Why |
|---|---|---|---|
| expected | `order_items.created_at, shipped_at` | 33,766 | Many items have a shipped time earlier than the item's created time. This is a known quirk of how the dates were generated. The order-level date is the one to use. These columns are not used in the KPIs. |
| expected | `order_items.created_at, delivered_at` | 5,761 | Many items have a delivered time earlier than the item's created time. It comes from the same date-generation quirk as finding 8. The brief does not use delivered_at. Delivery status is what matters. |
| expected | `users.email` | 25,534 | Customers sharing an email is not an error for this analysis. The brief does not count customers. |
| false alarm | `users.state` | 5 | Kagawa and Kanagawa are two different Japanese prefectures. Location is not used in the brief. |
| false alarm | `users.country` | 2 | Austria and Australia are two different countries. Location is not used in the brief. |
