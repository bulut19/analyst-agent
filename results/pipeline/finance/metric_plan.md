# Metric Plan

**Time window:** 2019-01-01 to 2026-09-30. Calendar quarters from Q1 2019 to Q3 2026 (31 quarters). Data starts on 2019-01-13, so Q1 2019 is partial. 2026-09-30 is treated as today and is the cut-off. Items with an order date after 2026-09-30 are left out. Default view: last 8 quarters, 2024-10-01 to 2026-09-30. Prior-year quarters back to 2023-10-01 are still loaded so year-over-year can be computed.

**Rules applied to every metric:**

- Source: order_items joined to products on order_items.product_id = products.id (inner join). No join to orders or users.
- Grain of the source: one row per order item. Each item is one unit, so cost is counted once per item.
- Period: calendar quarter (Q1 = Jan-Mar, Q2 = Apr-Jun, Q3 = Jul-Sep, Q4 = Oct-Dec) of order_items.created_at, in UTC as stored. Keep items with created_at >= 2019-01-01 and created_at < 2026-10-01.
- Kept items only: keep items where status is Complete, Shipped or Processing. Leave out status Cancelled and Returned. Use order_items.status, not orders.status.
- Also leave out any item with a non-null returned_at, even if its status looks different. Identify returns by status or by non-null returned_at, never by the return date. Do not use returned_at for timing.
- Leave out items with sale_price <= 0 (five rows, down to -$120). Log these rows and their dollar amount for review.
- Leave out items whose product_id has no match in products (five rows, product IDs 30001-30005). They have no department and no cost. Log row count and dollars excluded.
- Department comes from products.department only (Men or Women). Never use users.gender or orders.gender, which describe the customer.
- Do not use shipped_at or delivered_at anywhere. They are unreliable (dates before the order date). Do not delete those rows.
- Revenue uses order_items.sale_price, the actual price paid per item. It does not use the list retail price. No tax or shipping columns exist.
- Cost uses products.cost, which is one current value per product. Past margins are therefore restated at today's cost. Show this note on the dashboard.
- Gross margin % is always a ratio of sums (total margin divided by total revenue). Never average item-level percentages.
- Category spelling issues do not touch any KPI. Category is not used.
- Dashboard notes to show: (1) Q1 2019 is a partial quarter starting 2019-01-13. (2) Status is the current status, so past quarters can fall slightly as late returns arrive. (3) Recent quarters hold more Shipped and Processing items that may later be cancelled or returned, so they may look better than settled quarters.
- Result tables are small: at most 31 quarters x 3 rows (Men, Women, Both). No raw rows are listed.

## 1. Revenue

*How much money did we make from kept items in Men's and Women's each quarter?*

- **Formula:** Sum of order_items.sale_price over kept items (status Complete, Shipped or Processing; no return; sale_price > 0; product found), for each quarter and department. The 'Both' row is the Men plus Women total.
- **Grain:** One row per quarter x department (Men, Women, Both).
- **Breakdowns:** Quarter, Department (Men, Women, Both)
- **Filters:** products.department in ('Men','Women'); default shows both; Year or quarter range; default is the last 8 quarters (2024-10-01 to 2026-09-30); All shared rules
- **Time logic:** Period set by calendar quarter of order_items.created_at (UTC), from 2019-01-01 to 2026-09-30 inclusive. Q1 2019 starts 2019-01-13 (first data). Q3 2026 covers 2026-07-01 to 2026-09-30 and is labeled 'Q3 2026, to 30 Sep 2026'.
- **Cleaning:** Apply all shared rules.; Revenue is zero or missing for a quarter and department: show blank, not zero, if no kept items exist.
- **Excluded example:** A Women's dress ordered on 2025-08-14 whose status is Returned is left out of Q3 2025 revenue.

## 2. Gross margin ($)

*How many dollars are left after product cost, for Men's and Women's each quarter?*

- **Formula:** Sum of order_items.sale_price minus sum of products.cost, over the same kept items as Revenue, for each quarter and department.
- **Grain:** One row per quarter x department (Men, Women, Both).
- **Breakdowns:** Quarter, Department (Men, Women, Both)
- **Filters:** products.department in ('Men','Women'); default shows both; Year or quarter range; default is the last 8 quarters; All shared rules
- **Time logic:** Same as Revenue: calendar quarter of order_items.created_at (UTC), 2019-01-01 to 2026-09-30 inclusive.
- **Cleaning:** Apply all shared rules.; Cost is taken only from items that are in revenue. Cancelled and returned items add no cost.
- **Excluded example:** A Men's jacket with status Cancelled is left out of both its sale price and its cost. An item with a missing product record (ID 30002) is left out because it has no cost.

## 3. Gross margin (%)

*What share of each sales dollar is left after product cost, for Men's and Women's each quarter?*

- **Formula:** Gross margin ($) divided by Revenue, for the same quarter and department. Both are sums over the same kept items. Shown as a percent.
- **Grain:** One row per quarter x department (Men, Women, Both).
- **Breakdowns:** Quarter, Department (Men, Women, Both)
- **Filters:** products.department in ('Men','Women'); default shows both; Year or quarter range; default is the last 8 quarters; All shared rules
- **Time logic:** Same as Revenue: calendar quarter of order_items.created_at (UTC), 2019-01-01 to 2026-09-30 inclusive.
- **Cleaning:** Apply all shared rules.; Divide the sums. Do not average item-level percentages.; If revenue is zero or missing, show blank.
- **Excluded example:** An item with a sale price of $0 (a possible free gift) is left out of revenue and cost, so it does not change the margin %.

## 4. Year-over-year change

*Is each quarter better or worse than the same quarter one year earlier, for revenue and gross margin?*

- **Formula:** Three columns per row. (1) Revenue change % = (revenue this quarter - revenue same quarter prior year) / revenue same quarter prior year. (2) Gross margin $ change % = same formula on Gross margin ($). (3) Gross margin % change in percentage points = Gross margin % this quarter minus Gross margin % same quarter prior year. Revenue and margin inputs are the metrics defined above.
- **Grain:** One row per quarter x department (Men, Women, Both), from Q1 2020.
- **Breakdowns:** Quarter, Department (Men, Women, Both)
- **Filters:** products.department in ('Men','Women'); default shows both; Year or quarter range; default is the last 8 quarters. Prior-year quarters are loaded even when outside the range.; All shared rules
- **Time logic:** Each quarter is compared with the same quarter one year earlier (Q1 2026 vs Q1 2025). Q3 2026 is 2026-07-01 to 2026-09-30, compared with the same span 2025-07-01 to 2025-09-30. Order date is order_items.created_at. The Q3 2026 data ends on the cut-off, so it matches the full quarter. It is still labeled 'to 30 Sep 2026'.
- **Cleaning:** Apply all shared rules.; 2019 quarters have no prior year: show blank.; If the prior-year value is zero or missing, show blank.; Q1 2020 is compared with partial Q1 2019 (starts 2019-01-13). Show it with a flag: 'Prior quarter is partial; change is overstated'.; Do not round before computing. Round only for display.
- **Excluded example:** All 2019 quarters are left out of the YoY table because there is no 2018 data to compare with.

## Decisions assumed (please confirm)

- Items with sale_price <= 0 (five rows) are left out of revenue, cost and margin, and logged. Recommended option chosen; we do not know if they are errors, refunds or free gifts.
- Items whose product is missing from the product table (five rows) are left out of all KPIs and logged. No decision was needed.
- 'Kept' means status Complete, Shipped or Processing. Cancelled and Returned are left out. Processing and Shipped may still change. An optional Complete-only view is not built unless you ask.
- Items with a non-null returned_at are also left out, even if the status says otherwise.
- Department comes from the product (products.department). Only Men and Women exist, so nothing else is left out.
- Quarters are calendar quarters. Please confirm if the fiscal year differs.
- Revenue is placed in a quarter by order_items.created_at (the item's order date), not by shipping or delivery. Using orders.created_at could move a few items across a quarter edge.
- Revenue is the actual sale price, before tax and shipping. No such columns exist, so we cannot check this against the finance definition. Please ask finance to confirm.
- Cost is the current product cost, not the cost at the time of sale. The data has no cost history. A note is shown on the dashboard.
- Q3 2026 cut-off is 2026-09-30, treated as today. It is compared with 2025-07-01 to 2025-09-30. Because the data ends on the last day of the quarter, this is the full quarter. It is still labeled 'to 30 Sep 2026'. Please confirm the cut-off.
- Returned items are excluded from the quarter in which they were ordered, so past quarters can change slightly as late returns arrive.
- Data from 2019 is included for the long trend. The default view is the last 8 quarters (Q4 2024 to Q3 2026).
- YoY starts at Q1 2020 and is flagged because Q1 2019 is partial. 2019 quarters show blank YoY.
- A 'Both' row (Men plus Women) is added to each table for the 'both' filter. Its percentages are computed from combined sums.
- Gross margin $ change is shown in % and gross margin % change in percentage points, as the brief says.
