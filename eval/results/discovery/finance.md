# finance

**Business question:** Are Men's and Women's revenue and gross margin improving year over year, quarter by quarter?

# Data Mapping

| Item | Type | Columns | Logic |
|---|---|---|---|
| Revenue | kpi | `order_items.sale_price`, `order_items.status`, `order_items.created_at`, `order_items.product_id`, `products.id`, `products.department` | Grain is one row per order item. Sum order_items.sale_price where order_items.status is not Cancelled and not Returned. That keeps Complete, Shipped and Processing. Group by quarter of order_items.created_at and by products.department. |
| Gross margin ($) | kpi | `order_items.sale_price`, `products.cost`, `order_items.status`, `order_items.created_at`, `order_items.product_id`, `products.id` | Same item filter as Revenue (exclude Cancelled and Returned). Gross margin $ = SUM(order_items.sale_price) - SUM(products.cost). Each item row is one unit, so cost is counted once per item. Group by quarter and department. |
| Gross margin (%) | kpi | `order_items.sale_price`, `products.cost`, `order_items.status`, `order_items.created_at` | Gross margin $ divided by Revenue, both summed over the same kept items in the same quarter and department. Divide the sums. Do not average item-level percentages. Show nothing if revenue is zero. |
| Year-over-year change | kpi | `order_items.sale_price`, `products.cost`, `order_items.status`, `order_items.created_at` | Compute Revenue, Gross margin $ and Gross margin % per quarter and department. Compare each to the same quarter one year earlier. Revenue change % = (this - prior) / prior. Gross margin $ change can use the same % formula. Gross margin % change = this % minus prior %, in percentage points. 2019 quarters have no prior year, so show blank. |
| Quarter | dimension | `order_items.created_at` | Calendar quarter of order_items.created_at (Q1 = Jan to Mar). Quarter boundaries are in UTC, as stored. |
| Department: Men's vs. Women's | dimension | `products.department`, `order_items.product_id`, `products.id` | Join each item to its product and use products.department (Men or Women). Do not use users.gender or orders.gender. Those describe the customer, not the product department. |
| Filter: Department (Men's, Women's, or both) | filter | `products.department` | Filter on products.department in ('Men','Women'). Both is the default. Only these two values exist in the data. |
| Filter: Year or quarter range | filter | `order_items.created_at` | Filter on the quarter or year derived from order_items.created_at. Suggested default: the last 4 to 8 quarters. A year-over-year comparison needs the prior-year quarter loaded too, even when it is outside the selected range. |
| Time range: quarterly 2019 to Q3 2026 (Q3 shown quarter-to-date) | time_range | `order_items.created_at` | Include items from 2019-01-01 up to the cut-off date in Q3 2026 (July to September). Exclude any item created after 2026-09-30, because some rows run into early October 2026 (Q4). For the quarter-to-date comparison, use the same day span in Q3 2025, for example July 1 to the cut-off day. |

## Joins

- `order_items.product_id = products.id (needed for department and cost)`
- `No join to orders or users is needed. Revenue, cost, status and date are all available from order_items plus products.`

## Gaps

- **Cost at the time of sale:** products.cost is one current value per product. The data has no cost history. If costs changed over time, past gross margin is restated at today's cost. *Substitute:* Use products.cost as-is and note this on the dashboard.
- **Revenue 'before tax and shipping':** There are no tax or shipping columns. sale_price is the item price, so it excludes them by construction. We cannot check that it matches the finance definition. *Substitute:* Use order_items.sale_price. Ask finance to confirm.
- **Year-over-year change for 2019 quarters:** The data starts on 2019-01-13. There is no 2018 data, so no 2019 quarter has a prior-year comparison. *Substitute:* Show YoY from Q1 2020. Q1 2019 is also a partial quarter, which makes Q1 2020 YoY look larger than the true change.
- **Quarter-to-date for Q3 2026:** Order dates in the data end on 2026-09-30, so Q3 2026 looks complete. The brief calls it quarter-to-date, but the data does not say today's date or the cut-off. *Substitute:* Please confirm the cut-off date. Until then, compare the same day span in Q3 2025 as the brief says.
- **Items 'the customer kept':** The data has no 'kept' flag. Only Complete means delivered and kept. Shipped and Processing items are not yet final, and the brief only excludes Cancelled and Returned. *Substitute:* Include Complete, Shipped and Processing. Optionally show Complete only as a stricter view. Needs a decision.
- **Fiscal year:** The data has no fiscal calendar. *Substitute:* Use calendar quarters, as assumed in the brief.

## Data notes

- Use order_items.status, not orders.status. Status is recorded per item, and items in one order can differ.
- Status is the current status, not the status at the time. A past quarter's revenue can fall as late returns arrive. returned_at runs to 2026-10-08, after the last order date.
- Recent quarters hold more Shipped and Processing items, which may later be cancelled or returned. Recent revenue may be overstated compared with older, settled quarters, which can distort YoY.
- order_items.created_at runs to 2026-10-04, but orders.created_at ends 2026-09-30. Cap the data at the Q3 cut-off so October items do not leak in.
- Item dates and order dates can differ slightly. This mapping uses order_items.created_at as the order date, which avoids a join and keeps the period tied to the item. Using orders.created_at is an alternative but could move a few items across a quarter boundary.
- products.department has only Men and Women. The brief's 'other departments are left out' rule does not remove anything.
- Department is a product attribute. orders.gender and users.gender are customer gender, and a Women's customer can buy Men's items. Do not mix them.
- Gross margin % should be a ratio of sums. Averaging item-level margins would give wrong results.
- The first quarter, Q1 2019, starts on 2019-01-13, so it is a partial quarter.
- Customer personal fields (names, email) are not used.

*Column check: All columns exist in the schema.*
