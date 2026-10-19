# Metric Plan

**Time window:** 2025-01-01 to 2026-09-30. Q1 2025 to Q3 2026, using calendar quarters in UTC. Items are placed by order_items.created_at. Q4 2026 and full-year 2026 are left out because the data ends on 2026-09-30. Item dates run into early October 2026, so those rows are cut off at 2026-09-30 23:59:59.

**Rules applied to every metric:**

- Base table is order_items. Join each item to products on order_items.product_id = products.id to get cost and department.
- Count only items whose status is not 'Cancelled' and not 'Returned'. That keeps Complete, Shipped and Processing. If status is missing, treat the item as returned when returned_at is not null. Do not use the timing of returned_at, shipped_at or delivered_at.
- Exclude items with sale_price <= 0 (5 items). Log their count and value in the pipeline notes.
- Exclude items with no matching product record (product_id 30001-30005, 5 items). Log their count and value in the pipeline notes. This keeps Total equal to Men plus Women.
- Place each item in a quarter by order_items.created_at (UTC). Keep 2025-01-01 up to but not including 2026-10-01. Quarters are calendar quarters: Q1 Jan-Mar, Q2 Apr-Jun, Q3 Jul-Sep.
- Department comes from products.department (Men or Women). Never use the customer's gender from orders or users.
- Do not join to orders. Do not show any personal fields.
- The Total row is computed from summed Men plus Women amounts. Ratios are always computed from summed amounts, never by averaging or adding percentages.
- Year-over-year change compares each 2026 period with the same period of 2025. Absolute change is 2026 minus 2025. % change is the absolute change divided by the 2025 value.
- Amounts are in US dollars, rounded for display only. Do not round before calculating ratios.
- Label on the dashboard: revenue is item sales before tax and shipping. Margin uses each product's current cost, not the cost at the time of sale. Recent quarters, especially Q3 2026, may be overstated because Shipped and Processing items can still be returned or cancelled.

## 1. Revenue

*How much did we sell in each quarter of 2026 compared with the same quarter of 2025, in total and for Men and Women?*

- **Formula:** Sum of order_items.sale_price for items that pass the shared rules (status not Cancelled or Returned, sale_price > 0, product found). YoY absolute change = 2026 revenue minus 2025 revenue. YoY % change = absolute change divided by 2025 revenue.
- **Grain:** One row per period (Q1, Q2, Q3 and Jan-Sep year-to-date) x year (2025, 2026) x department view (Men, Women, Total). That is 24 rows. The YoY columns are filled on the 2026 rows.
- **Breakdowns:** Quarter, Year, Department view: Men, Women, Total
- **Filters:** Year (2025, 2026); Department (Men, Women, both)
- **Time logic:** Quarter from order_items.created_at (UTC). Quarters run Q1 2025 to Q3 2026. Year-to-date is 2025-01-01 to 2025-09-30 against 2026-01-01 to 2026-09-30.
- **Cleaning:** Apply all shared rules.; If a department and quarter has no qualifying items, revenue is 0. If the 2025 value is 0, show the YoY % change as 'n/a', not a number.
- **Excluded example:** A 2026 Q2 item with status Returned and a sale price of $60 is not counted. Neither is an item dated 2026-10-02.

## 2. Gross margin (amount)

*How many dollars of profit on product cost did we make in each quarter of 2026 compared with 2025, in total and for Men and Women?*

- **Formula:** Sum of (order_items.sale_price minus products.cost) for the same items as Revenue. This equals Revenue minus product cost. YoY absolute change = 2026 margin minus 2025 margin. YoY % change = absolute change divided by 2025 margin amount.
- **Grain:** One row per period (Q1, Q2, Q3 and Jan-Sep year-to-date) x year (2025, 2026) x department view (Men, Women, Total). That is 24 rows. The YoY columns are filled on the 2026 rows.
- **Breakdowns:** Quarter, Year, Department view: Men, Women, Total
- **Filters:** Year (2025, 2026); Department (Men, Women, both)
- **Time logic:** Quarter from order_items.created_at (UTC). Quarters run Q1 2025 to Q3 2026. Year-to-date is 2025-01-01 to 2025-09-30 against 2026-01-01 to 2026-09-30.
- **Cleaning:** Apply all shared rules.; Use the same item set as Revenue, so margin and revenue always match row for row.; Skip any item with a missing cost from both Revenue and margin, so the two stay consistent. Log the count.; If the 2025 margin is 0 or less, show the YoY % change as 'n/a'. Still show the absolute change.
- **Excluded example:** An item with a product_id that has no product record (for example 30003) is left out, because it has no cost and no department.

## 3. Gross margin %

*What share of revenue is left after product cost in each quarter, and did it improve or fall compared with 2025?*

- **Formula:** Gross margin amount divided by Revenue, both summed over the same items, quarter and department view. YoY change is shown in percentage points: 2026 margin % minus 2025 margin %. Total and year-to-date are recalculated from summed amounts.
- **Grain:** One row per period (Q1, Q2, Q3 and Jan-Sep year-to-date) x year (2025, 2026) x department view (Men, Women, Total). That is 24 rows. The YoY change in percentage points is filled on the 2026 rows.
- **Breakdowns:** Quarter, Year, Department view: Men, Women, Total
- **Filters:** Year (2025, 2026); Department (Men, Women, both)
- **Time logic:** Quarter from order_items.created_at (UTC). Quarters run Q1 2025 to Q3 2026. Year-to-date is 2025-01-01 to 2025-09-30 against 2026-01-01 to 2026-09-30.
- **Cleaning:** Apply all shared rules.; Never average item-level or quarterly percentages.; If revenue is 0 for a row, leave the margin % empty and label it 'no sales'. Do not show 0%. Leave the YoY point change empty if either year is 'no sales'.
- **Excluded example:** A Processing item is kept, but a Cancelled item is excluded from both the margin amount and the revenue in the ratio.

## Decisions assumed (please confirm)

- Shipped and Processing items count as revenue. Only Cancelled and Returned are excluded, as in the brief. Because these items can still be returned, Q3 2026 may be slightly overstated. A note is shown. If you prefer Complete only, the figures will fall, most for the latest quarter.
- Items with a sale price of zero or below (5 items) are left out of revenue and margin. They are treated as errors or non-sales.
- The 5 items with no product record (ids 30001-30005) are left out of all figures, so Total equals Men plus Women. The count and value are reported in a footnote.
- Gross margin is sale price minus the product's current cost, because the data has no cost history. It is labelled as based on current cost.
- Quarters are calendar quarters (Jan-Mar, Apr-Jun, Jul-Sep). Please confirm this matches the fiscal year.
- Items are dated by order_items.created_at in UTC, used as the order date. Orders are not joined, because some orders are missing from the orders table.
- Q3 2026 is treated as complete because the last order is at 23:59 on 30 Sep 2026.
- Revenue is item sales before tax and shipping. The data has no tax, shipping or discount fields.
- A year-to-date view (Jan-Sep 2026 vs Jan-Sep 2025) is added as a summary. Please approve or remove it.
- Gross margin % change is shown in percentage points, not as a % change.
- Where there is nothing to divide by: margin % shows 'no sales' when revenue is 0. YoY % change shows 'n/a' when the 2025 base is 0 or, for margin, 0 or less.
- Shipped, delivered and returned dates are unreliable and are not used. Returned items are identified by status.
- Product category spelling fixes are not needed here, because the dashboard uses department only.
