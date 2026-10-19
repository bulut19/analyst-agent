# Data Quality Audit

Two problems could change which products get flagged. The first is five misspelled category names, which split products out of their real category. The second is five order items with a zero or negative sale price, which distort margin. The other findings have little effect on this brief. The three date-order checks cover columns the KPIs don't use. The five items with unknown products can't appear in the product list.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| high | `products.category` | 5 | Five products have a misspelled category, such as 'jeans ' or 'Sweater'. The ranking would treat each as a separate tiny category. A product alone in its category lands in the bottom 10% automatically, so it gets flagged if its margin is under 20%. The real categories also lose those products, so their ranks shift. The category filter and the per-category candidate counts would be wrong too. | Trim spaces and standardise case on products.category, then map: 'JEANS' and 'jeans ' to 'Jeans'; 'Tops and Tees' to 'Tops & Tees'; 'Sweater' to 'Sweaters'; 'Accesories' to 'Accessories'. Do this before ranking. Then check that no category has only one product. |
| medium | `order_items.sale_price` | 5 | Five order items have a zero or negative sale price. Margin uses the real price paid, so a -120 line can wipe out the revenue of a slow product. Slow products have few sales, which are the products this dashboard targets. A zero price could be a real free giveaway. A negative price is not a sale and looks like a refund or an entry error. | Exclude order items with sale_price < 0 from units sold and margin. Hold the sale_price = 0 rows out of the numbers until the stakeholder answers. List the excluded rows in a data notes section. |
| low | `order_items.product_id` | 5 | Five order items point to product IDs (30001 to 30005) that are not in the product list. We have no category or cost for them, so we can't rank them or work out their margin. They won't appear in the product table. They don't change any product's numbers, but they are lost sales. | Inner join order_items to products on product_id. Drop the orphan rows from the dashboard and report their count in a data notes section. Ask the data owner to find the missing products. |
| low | `order_items.created_at, shipped_at` | 33,766 | About 33,800 items show a ship date before the order date. That can't happen, so the timestamps are unreliable. This brief doesn't use ship dates. The only date it needs is the order date, for the 12-month window. | No exclusion. Don't use shipped_at in any KPI. Note the problem for the data owner. |
| low | `order_items.created_at, delivered_at` | 5,761 | About 5,800 items show a delivery date before the order date. The timestamps are wrong, but the brief doesn't use delivery dates. | No exclusion. Don't use delivered_at in any KPI. Note the problem for the data owner. |
| low | `order_items.created_at, returned_at` | 637 | 637 items show a return date before the order date. Returns are out of scope for this dashboard, so no KPI is affected. | No exclusion. Don't use returned_at. Note the problem for the data owner in case returns are added later. |

## Decisions needed

- **order_items.sale_price:** Some items were sold at a price of 0. Are these real free gifts or promotions that should count as units sold at zero revenue, or are they errors to leave out? Negative prices will be left out unless you tell us otherwise.
