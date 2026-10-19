# Metric Plan

**Time window:** 2025-10-01 to 2026-09-30. The 12 complete calendar months ending at the data end (2026-09-30). A row belongs to the window if order_items.created_at is on or after 2025-10-01 00:00 UTC and before 2026-10-01 00:00 UTC. order_items runs to 2026-10-04, so items from October 2026 are left out as a partial month.

**Rules applied to every metric:**

- Source: order_items joined to products on order_items.product_id = products.id. Do not join orders or users. Status comes from order_items.status, not orders.status.
- Period: order_items.created_at (UTC) from 2025-10-01 up to but not including 2026-10-01. Never use shipped_at, delivered_at or returned_at. These dates are unreliable.
- Items counted as sold: status in (Complete, Shipped, Processing, Returned). Status = 'Cancelled' is dropped. Returned items stay in, as the stakeholder asked. No return adjustment anywhere.
- Exclude items with sale_price <= 0 (about 5 rows). List them in a separate check table with product id, status, price and date.
- Exclude items whose product_id is not in products.id (product ids 30001 to 30005, 5 items). Show on the dashboard a data note with their count and excluded revenue.
- Clean products.category before grouping or filtering: trim whitespace; JEANS and 'jeans ' become Jeans; 'Tops and Tees' becomes 'Tops & Tees'; Sweater becomes Sweaters; Accesories becomes Accessories. Other overlapping categories (Socks vs Socks & Hosiery, Pants vs Pants & Capris, Suits vs Suits & Sport Coats) are NOT merged.
- Unit cost is products.cost, one current value per product. There is no cost history, so past sales use today's cost. State this on the dashboard.
- Product key is products.id. Show products.name only as a label, since names are not unique. Do not show brand or any customer data.
- Ranked set: products with at least one counted item in the window after all rules above. Products with no counted items are not in the ranking and are not shown. They can never be flagged.
- Order of work: clean items, then total per product, then compute the cut-off across ALL ranked products, then flag, then apply the Category and Candidate flag filters. Filters never change the cut-off or the flag.
- Because the full ranked set is large, result tables show at most 100 rows, sorted by units ascending, then margin % ascending, then product id. The cut-off and counts are always calculated on the full set, before the limit.

## 1. Units sold

*How many items of each product did we sell in the last 12 months?*

- **Formula:** Numerator: count of order_items rows (order_items.id) per product_id after the shared cleaning rules. Statuses Complete, Shipped, Processing and Returned count. Cancelled does not. There is no denominator. Products with zero counted items do not appear (no row, not a zero).
- **Grain:** One row per product (products.id), with product name and cleaned category.
- **Breakdowns:** Category (grouped list), Product (products.id, name as label)
- **Filters:** Category; Candidate flag (candidates only or all products); Window 2025-10-01 to 2026-09-30; Max 100 rows, lowest units first
- **Time logic:** order_items.created_at >= 2025-10-01 and < 2026-10-01 (UTC). The item's own created_at places it in the period.
- **Cleaning:** Drop Cancelled items.; Drop items with sale_price <= 0.; Drop items whose product_id is not in products.; Do not subtract returns.
- **Excluded example:** A Cancelled item for a jacket ordered in January 2026 is not counted. Nor is an item with sale_price = -120.

## 2. Revenue

*How much money did each product bring in over the last 12 months, using the price customers actually paid?*

- **Formula:** Sum of order_items.sale_price per product_id over the same items counted in Units sold. Do not use products.retail_price. Returned items stay in. No denominator. Products with no counted items do not appear.
- **Grain:** One row per product (products.id), with product name and cleaned category.
- **Breakdowns:** Category (grouped list), Product (products.id, name as label)
- **Filters:** Category; Candidate flag (candidates only or all products); Window 2025-10-01 to 2026-09-30; Max 100 rows, lowest units first
- **Time logic:** order_items.created_at >= 2025-10-01 and < 2026-10-01 (UTC).
- **Cleaning:** Same item filter as Units sold.; Items with sale_price <= 0 are excluded so they cannot pull revenue down.; Show money rounded to 2 decimals.
- **Excluded example:** A Returned item is NOT excluded (its price stays in revenue). A Cancelled item priced at 45.00 is excluded.

## 3. Margin %

*After product cost, what share of each product's revenue is left as margin?*

- **Formula:** (Revenue - total cost) / Revenue, per product. Revenue = sum of sale_price over counted items. Total cost = sum of products.cost over the same counted items (unit cost x units sold). Use the unrounded value in tests. Show as a percent with 1 decimal. It can be negative. Nothing to divide by: revenue is always above 0 for any product in the ranking, because items with price <= 0 are removed and each product has at least one item. A product with no counted items has no row and no margin. It is not shown as 0%.
- **Grain:** One row per product (products.id), with product name and cleaned category.
- **Breakdowns:** Category (grouped list), Product (products.id, name as label)
- **Filters:** Category; Candidate flag (candidates only or all products); Window 2025-10-01 to 2026-09-30; Max 100 rows, lowest units first
- **Time logic:** order_items.created_at >= 2025-10-01 and < 2026-10-01 (UTC).
- **Cleaning:** Same item filter as Units sold.; Use actual sale_price, not retail_price.; Use current products.cost. Items with no matching product are excluded, so cost is never missing.; If a divide by zero ever occurs, return no value and do not flag the product.
- **Excluded example:** A product that sold only Cancelled items in the window has no margin and is left out. An item for a product id not in products is left out because its cost is unknown.

## 4. Discontinuation candidate flag

*Which products are in the bottom 10% by units sold AND have margin below 20%?*

- **Formula:** Step 1: take all ranked products (at least 1 counted item). Step 2: cut-off = 10th percentile of units sold across all these products, using PERCENTILE_CONT(0.1), not split by category. Step 3: flag = 1 if units <= cut-off AND margin % < 0.20 (strictly below, unrounded). Ties at the cut-off are all included. Output also three summary figures: the cut-off value, the number of ranked products, and the number of flagged products with their share of ranked products. If there are no ranked products, show 'No sales in period' and no flags.
- **Grain:** One row per product (products.id) with units, revenue, margin %, flag (Yes/No), cleaned category and name. Plus one summary row with cut-off, ranked count and flagged count.
- **Breakdowns:** Category (grouped list), Product (products.id, name as label)
- **Filters:** Category (applied after the flag); Candidate flag: candidates only (default) or all products; Max 100 rows, lowest units first
- **Time logic:** Uses the Units sold and Margin % results for order_items.created_at >= 2025-10-01 and < 2026-10-01 (UTC). The cut-off is fixed on the full window and full ranked set.
- **Cleaning:** All shared rules apply.; Products with zero counted items are not ranked and never flagged.; Show the cut-off value on the dashboard. Many products may share it, so the flagged group can be larger than 10%.
- **Excluded example:** A product with 40 units and a 5% margin is not flagged (units above the cut-off). A product with 1 unit and a 45% margin is not flagged (margin not below 20%). A product with no sales in the window is not ranked at all.

## Decisions assumed (please confirm)

- Items with sale_price <= 0 are treated as data errors or non-sales and excluded from all KPIs, with a check table listing them (audit decision, recommended option).
- Items pointing to product ids missing from products (30001 to 30005) are excluded and noted on the dashboard with their count and revenue. We assume the product team cannot supply them (audit decision, recommended option).
- Cancelled items are excluded from units and revenue. Returned items stay in, as requested.
- Shipped and Processing items count as sold, along with Complete and Returned. Please confirm, since some late September items may not be final.
- Margin % uses actual sale price and current product cost, not list price.
- The bottom 10% is ranked across all products with at least one sale, not within each category.
- Products with zero sales in the window are excluded from the ranking and not shown. The data has no flag for whether a product was still on offer.
- New launches are included on the same basis as other products. The data has no launch date, so we cannot mark them. A first-order-date proxy is possible if you want an exclusion.
- 'Last 12 months' is 2025-10-01 to 2026-09-30. We assume September 2026 is complete, because the last order is at 23:59 on 30 September. October 2026 items are excluded.
- Ties at the cut-off are all included (units <= cut-off). The cut-off is calculated with PERCENTILE_CONT(0.1). The share flagged is shown so you can check whether ties make the list too large.
- Margin below 20% means strictly below, on the unrounded value. Negative margins qualify.
- A product with no sales gets no margin and no flag, and is not shown as 0% or as a candidate. Products with no sales are shown nowhere.
- Overlapping categories (Socks vs Socks & Hosiery, Pants vs Pants & Capris, Suits vs Suits & Sport Coats) stay as separate groups until the team approves a merge. Obvious typos are fixed.
- Tables are limited to 100 rows, lowest units first then lowest margin, to keep them readable. Candidates only is the default view.
- Months are cut in UTC time, not local business time.
- Shipping, delivery and return dates are not used because the audit found them unreliable.
