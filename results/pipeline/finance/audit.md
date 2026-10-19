# Data Quality Audit

Two problems could change the board's numbers. Five order items have zero or negative prices, and five order items point to products that don't exist, so we can't tell if they are Men's or Women's. The date-order and spelling problems are real data errors, but this dashboard doesn't use those fields, so they are low risk. I need one decision from you, on the zero and negative prices.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| medium | `order_items.sale_price` | 5 | Five items have a zero or negative sale price (down to -$120). A real sale can't have a negative price. These would pull revenue down, or add cost with no revenue, and so distort margin in their quarter. The number of rows is small, but the data is clearly wrong. We don't know yet if the negatives are refunds or errors, or if the zeros are free gifts. | Exclude order items with sale_price <= 0 from revenue, cost and margin. Log the excluded rows and their dollar amount for review. |
| medium | `order_items.product_id` | 5 | Five order items point to product IDs 30001-30005, which are not in the product table. We can't tell their department or their cost. We can't assign them to Men's or Women's. If they were kept in revenue with no cost, they would inflate margin. | Exclude order items whose product_id has no match in products from all KPIs, since they have no department and no cost. Report how many rows and how many dollars were excluded. |
| low | `order_items.created_at, shipped_at` | 33,766 | About 34,000 items show a shipped date before the order date. That is impossible, so the shipping timestamps are unreliable. The dashboard uses only the order date, so no KPI is affected. | Don't use shipped_at in any KPI. Don't delete these rows. Don't add shipping-time metrics without fixing the data first. |
| low | `order_items.created_at, delivered_at` | 5,761 | About 5,800 items show a delivered date before the order date. This is the same kind of timestamp error as the shipped dates. Revenue is counted by order date and doesn't use delivery, so the KPIs are not affected. | Don't use delivered_at in any KPI. Don't delete these rows. Don't add delivery-time metrics without fixing the data first. |
| low | `order_items.created_at, returned_at` | 637 | 637 returned items have a return date before the order date. The return date is wrong. The brief excludes returned items by their order quarter, so the date doesn't change which quarter they land in. It only matters if a returned item was missing its return status. The risk is small. | Identify returned items by item status, or by a non-null returned_at, not by the return date. Exclude them from the quarter of the order date. Don't use returned_at for timing. |
| low | `products.category` | 5 | Five products have category names with typos or odd spacing, such as 'jeans ' and 'Accesories'. These are the same categories as the standard spellings. The dashboard splits by department, not category, so no KPI is affected. It would matter if category were added later. | Trim spaces and map variants to the standard names: JEANS and 'jeans ' to Jeans, 'Tops and Tees' to 'Tops & Tees', Sweater to Sweaters, Accesories to Accessories. Not needed for the current KPIs. |

## Decisions needed

- **order_items.sale_price:** Five items have a zero or negative sale price. Are these errors, refunds, or free gifts? I suggest leaving them out of revenue and margin. Do you agree?
