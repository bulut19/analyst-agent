# Metric Plan

**Time window:** 2025-01-01 to 2026-09-30. Q1–Q3 2025 (2025-01-01 to 2025-09-30) and Q1–Q3 2026 (2026-01-01 to 2026-09-30). Q4 2025 falls between them and is not shown. Q3 2026 is labelled 'through September' because it may not be final. Rows dated 2026-10-01 or later are left out.

**Rules applied to every metric:**

- Base table: order_items joined to products on order_items.product_id = products.id (inner join). Items with no matching product (IDs 30001–30005) are left out of every metric. Log their count and sale_price total.
- Quarter and year come only from order_items.created_at, in UTC. Calendar quarters: Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep. Keep rows where created_at is in [2025-01-01, 2025-10-01) or [2026-01-01, 2026-10-01). Do not use orders.created_at, shipped_at, delivered_at or returned_at for timing.
- Department is products.department. Keep only 'Men' and 'Women' (shown as Men's and Women's). Never use users.gender or orders.gender.
- Kept items = items with status not 'Cancelled' and not 'Returned', and returned_at is null. This keeps Complete, Shipped and Processing. Use order_items.status, not orders.status. Returned items are found by status or a non-null returned_at, never by the returned_at date (637 items have a return date before the order date).
- Leave out items with sale_price <= 0 (5 items). Log the count and dollar total per quarter in an internal log or footnote.
- Leave out items where products.cost is null. Never treat a missing cost as zero. Revenue and margin use exactly the same set of items, so the margin % is always on the same base.
- Do not drop rows because of bad ship, delivery or return dates. Those columns are not used. Flag the date problems to the data owner.
- Dollar amounts come from summing item rows. Round only for display: dollars to the nearest dollar, percentages to one decimal place, margin % change to one decimal of a percentage point.
- Do not show customer names, emails or any personal data.
- Footnotes on the dashboard: (1) Q3 2026 is 'through September' and may not be final. (2) Late returns can lower past quarters, so figures may change. (3) Margin uses today's product cost for all sales, including 2025. (4) Revenue is item sale price only: no shipping, tax or extra discounts. (5) Shipped and Processing items count as revenue until returned.

## 1. Revenue

*How much did the Men's and Women's departments sell, by quarter, in 2026 compared with 2025?*

- **Formula:** Sum of order_items.sale_price over kept items (see shared rules). Kept items are not Cancelled, not Returned, sale_price > 0, matched to a product with a cost. Grouped by year, quarter and department. The combined row 'Men + Women' is the sum of the two departments' dollars.
- **Grain:** One row per year (2025, 2026) × quarter (Q1, Q2, Q3) × department (Men, Women, plus a combined 'Men + Women' row). 18 rows.
- **Breakdowns:** Year, Quarter, Product department (Men, Women, combined total)
- **Filters:** products.department in ('Men','Women'); created_at in 2025-01-01 to 2025-09-30 or 2026-01-01 to 2026-09-30; Viewer filters: department and quarter
- **Time logic:** Quarter and year from order_items.created_at (UTC). Q1 = 01-01 to 03-31, Q2 = 04-01 to 06-30, Q3 = 07-01 to 09-30. Q3 2026 ends 2026-09-30 and is labelled 'through September'. Rows are placed by the order date, not by ship or return date.
- **Cleaning:** Apply all shared rules.; Exclude created_at on or after 2026-10-01, even though order_items has rows up to 2026-10-04.
- **Excluded example:** A Women's item ordered on 2026-03-12 with status 'Returned' is left out of Q1 2026 revenue. So is an item ordered on 2026-10-02 (after the window).

## 2. Gross margin (dollars)

*How much profit on product cost did each department earn, by quarter, in 2026 compared with 2025?*

- **Formula:** Sum of (order_items.sale_price − products.cost) over exactly the same kept items as Revenue. Equal to Revenue minus the summed product cost of those items. Grouped by year, quarter and department. The combined row is the sum of the two departments.
- **Grain:** One row per year (2025, 2026) × quarter (Q1, Q2, Q3) × department (Men, Women, plus combined 'Men + Women'). 18 rows.
- **Breakdowns:** Year, Quarter, Product department (Men, Women, combined total)
- **Filters:** Same item set as Revenue; Viewer filters: department and quarter
- **Time logic:** Same as Revenue: quarter and year from order_items.created_at (UTC), window 2025-01-01 to 2025-09-30 and 2026-01-01 to 2026-09-30.
- **Cleaning:** Apply all shared rules.; Margin is not reduced by items with sale_price <= 0 because those are excluded.; Items with a cost above the sale price stay in and give a negative margin. Count them in the internal log.
- **Excluded example:** An item sold at 0.00 (a possible giveaway) is left out. If it were kept it would add cost with no revenue. An item with product_id 30003 (no matching product) is also left out, since it has no cost.

## 3. Gross margin %

*What share of revenue was left as gross margin, by quarter and department, in 2026 compared with 2025?*

- **Formula:** Gross margin (dollars) divided by Revenue, both summed first for the same year, quarter and department. Never average item-level percentages. The combined row uses the summed dollars of both departments. If Revenue is 0, return null.
- **Grain:** One row per year (2025, 2026) × quarter (Q1, Q2, Q3) × department (Men, Women, plus combined 'Men + Women'). 18 rows.
- **Breakdowns:** Year, Quarter, Product department (Men, Women, combined total)
- **Filters:** Same item set as Revenue and Gross margin (dollars); Viewer filters: department and quarter
- **Time logic:** Same as Revenue: quarter and year from order_items.created_at (UTC), window 2025-01-01 to 2025-09-30 and 2026-01-01 to 2026-09-30.
- **Cleaning:** Apply all shared rules.; Numerator and denominator must come from the same item set.
- **Excluded example:** A Cancelled Men's item ordered on 2025-08-05 is in neither the margin dollars nor the revenue, so it does not change the %.

## 4. Year-over-year change

*For each 2026 quarter, how far are Revenue, Gross margin dollars and Gross margin % from the same quarter of 2025?*

- **Formula:** For each 2026 quarter and department (and the combined total), using the aggregates above. Revenue change % = Revenue 2026 / Revenue 2025 − 1. Gross margin dollars change % = GM$ 2026 / GM$ 2025 − 1. Gross margin % change = GM% 2026 − GM% 2025, in percentage points (not a ratio). If the 2025 base is 0 or null, return null.
- **Grain:** One row per 2026 quarter (Q1, Q2, Q3) × department (Men, Women, plus combined 'Men + Women'). 9 rows, with three change columns.
- **Breakdowns:** Quarter, Product department (Men, Women, combined total)
- **Filters:** Same item set as the other metrics; Viewer filters: department and quarter
- **Time logic:** A 2026 quarter is matched to the same quarter number in 2025 (Q1 2026 vs Q1 2025, and so on). Both are placed by order_items.created_at (UTC). Q3 2026 covers 2026-07-01 to 2026-09-30 and is compared with the full Q3 2025 (2025-07-01 to 2025-09-30). Label it 'through September'.
- **Cleaning:** Apply all shared rules.; Compute from the summed aggregates, not from averaged rows.
- **Excluded example:** Q4 2025 is not used as a comparison, and no 2025 quarter is shown as a change row. A Returned item from Q2 2025 is already removed from the 2025 base.

## Decisions assumed (please confirm)

- Items with sale_price of zero or below (5 items): we leave them out of Revenue and margin, and log them. Please overrule if they are real sales.
- Items with no matching product (5 items, IDs 30001–30005): left out of all numbers. They look like test records.
- Status: we follow the brief and leave out only Cancelled and Returned items. Shipped and Processing items count as revenue. Q3 2026 has more in-transit items, which could flatter the 2026 comparison and change if they are later returned. The alternative is to count Complete items only. Please confirm.
- Gross margin = sale price minus the product cost on file. Cost is today's cost, not the cost at time of sale. Please confirm.
- Quarters are calendar quarters. Please confirm they match the company's fiscal year. The data cannot check this.
- Revenue is placed in the quarter the order was placed. Returns are removed from the original quarter, so past figures can change.
- Revenue is item sale price only. Shipping, tax and extra discounts are not in the data.
- Only Men's and Women's departments are shown. Any other department is left out.
- We include a combined 'Men + Women' total, built from summed dollars. Tell us if you do not want it.
- The 'on track' judgement is out of scope. There are no targets, so the dashboard compares with last year only.
- Ship, delivery and return dates are not used, so the date errors in them do not change any number.
