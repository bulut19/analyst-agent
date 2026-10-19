# Data Quality Audit

Two findings could change the board numbers. They are the 5 order items with zero or negative prices, and the 5 items whose product is missing from the product table. The other four are real data errors, but no KPI in this brief uses those fields. They need only light handling.

## Issues to fix

| Severity | Table.column | Rows | What is wrong | Proposed rule |
|---|---|---|---|---|
| medium | `order_items.sale_price` | 5 | Five items have a sale price of zero or below. A negative price would quietly reduce revenue. A zero price adds cost but no revenue, which lowers margin. They may be refunds, giveaways or entry errors, and the data does not say which. The dollar impact is small, but a few such rows can still shift a quarter's figures, especially margin %. | Exclude order items with sale_price <= 0 from Revenue and Gross margin. Report the count and dollar total of excluded rows per quarter in a footnote or internal log. |
| medium | `order_items.product_id` | 5 | Five order items point to product IDs (30001–30005) that do not exist in the product table. We cannot tell their department or cost. They cannot be placed in Men's or Women's. If kept with a blank cost, they would add revenue at a 100% margin and inflate margin. The IDs look like test or placeholder records. | Exclude order items whose product_id has no match in products from all KPIs (inner join to products). Log the count and sale_price total of the excluded rows. Do not treat a missing cost as zero. |
| low | `order_items.created_at, shipped_at` | 33,766 | About 33,800 items show a ship date before the order date, which is impossible. No KPI uses the ship date. Quarters are set by order date. The error suggests some timestamps are unreliable, but we cannot tell which one is wrong. The risk is small, limited to orders placed near a quarter boundary. | Do not use shipped_at in any KPI. Do not drop these rows. Keep assigning quarter by created_at. Flag the timestamp problem to the data owner. |
| low | `order_items.created_at, delivered_at` | 5,761 | About 5,800 items show a delivery date before the order date, which is impossible. The brief does not use delivery dates, so no KPI number changes. | Do not use delivered_at in any KPI. Do not drop these rows. Flag to the data owner. |
| low | `order_items.created_at, returned_at` | 637 | 637 items have a return date before the order date. The items are still marked as returned, so they are still excluded as the brief requires. The bad date matters only if we used the return date to place a return in a quarter. We use the order date, so the impact is minimal. | Identify returned items by returned_at being non-null, not by its date. Exclude them from Revenue and margin. Assign quarter by created_at only. Do not use returned_at for timing. |
| low | `products.category` | 5 | Five products have category names that are typos or variants of valid ones, such as 'JEANS', 'Sweater' and 'Accesories'. This would split categories in a category report. The brief reports by department, not category, so no KPI is affected. | Standardise category: trim spaces, fix case, and map 'JEANS' and 'jeans ' to 'Jeans', 'Tops and Tees' to 'Tops & Tees', 'Sweater' to 'Sweaters' and 'Accesories' to 'Accessories'. Not needed for this dashboard. |

## Decisions needed

- **order_items.sale_price:** Some items have a zero or negative sale price. Are these refunds, free gifts or mistakes? Should we leave them out of Revenue and margin (our proposal), or count them?
