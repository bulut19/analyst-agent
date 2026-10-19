# Metric Plan

**Time window:** 2019-01-01 to 2026-09-30. Customers are grouped by the year of their first valid order, 2019 to 2026. Only orders created on or before 2026-09-30 are used, as that is the last valid order date. 12-month view: first order on or before 2025-09-30 is 'complete' (12 full months observed). First order from 2025-10-01 onward is 'not yet complete: not final'. So 2025 appears in both sections. 6-month view (same-time comparison): first order on or before 2026-03-31 has 6 full months observed. First order from 2026-04-01 onward is 'not yet complete: not final'.

**Rules applied to every metric:**

- Source is the orders table, one row per order. order_items is not used.
- Valid order = status is not 'Cancelled', user_id is not null, and created_at is on or before 2026-09-30 23:59:59 UTC. Orders dated 2027 or 2028 are excluded and listed in an exceptions list. Returned, Complete, Shipped and Processing all count.
- Duplicate order_id: if the duplicate rows are identical, keep one. If they differ, keep the row with the earliest created_at and flag it. Count distinct order_id throughout.
- Orders with a null user_id are dropped from all customer calculations. The count is reported in the exceptions list.
- Apply the exclusions above BEFORE finding each customer's first order. So a customer whose first order was cancelled gets their next valid order as the first order.
- First order = the customer's valid order with the earliest created_at (UTC). Tie on the same timestamp: the lowest order_id is the first order.
- Customer group = year of the first order (UTC). It is set once per customer. Never filter orders by year before finding first and second orders.
- 12-month complete flag is set per customer: 'Complete' if first order created_at is on or before 2025-09-30 23:59:59. Otherwise 'Not yet complete: not final'.
- 6-month complete flag is set per customer: 'Complete' if first order created_at is on or before 2026-03-31 23:59:59. Otherwise 'Not yet complete: not final'.
- Location = users.country on file, from a left join on orders.user_id = users.id. 'United States' is its own group. Every other country is its own group. 'España' is merged into 'Spain'. A missing user row or null country becomes 'Unknown'. All ~15 countries are shown, no limit needed.
- Ratios are always computed as sum of repeaters divided by sum of first-time customers. Never average rates across locations or years.
- Every rate is shown beside its group size. Groups with fewer than 50 first-time customers carry a 'small group: rate may swing' flag.
- The 2019 group is labeled: 'may include customers who first ordered before 2019, as data starts in Jan 2019'.
- No personal data (name, email) appears on the dashboard. delivered_at, shipped_at and num_of_item are not used.

## 1. First-time customers (group size)

*How many customers made their first order in each year, and in each location?*

- **Formula:** Count of distinct user_id among valid customers, grouped by first-order year, completeness flag and location. Each customer is counted once, in the group of their first valid order.
- **Grain:** One row per first-order year x completeness flag x location. A second set of rows gives 'All locations' per year and flag, summed from the location rows.
- **Breakdowns:** Year of first order, Completeness flag (complete / not yet complete: not final), Location (United States, each other country, Unknown)
- **Filters:** Year of first order; Location
- **Time logic:** Place each customer by the year of their earliest valid orders.created_at (UTC), 2019 to 2026. Complete flag: first order on or before 2025-09-30. Not yet complete: first order from 2025-10-01 to 2026-09-30.
- **Cleaning:** Apply all shared rules.; Customers with no valid order are not in the base (never ordered, or all orders cancelled).
- **Excluded example:** A customer whose only order is Cancelled is not counted. A customer whose only order is dated 2027 is not counted.

## 2. Repeat customers

*How many first-time customers placed a second order within 12 months of their first order?*

- **Formula:** Count of distinct user_id where the customer has at least one other valid order (different order_id) with created_at strictly later than the first order's created_at and on or before first order created_at + 12 calendar months. Use a calendar-month function (e.g. DATETIME_ADD(..., INTERVAL 12 MONTH)), not 365 days. A same-day second order counts. Because only orders up to 2026-09-30 exist, not-yet-complete groups only count seconds observed so far.
- **Grain:** One row per first-order year x completeness flag x location, plus 'All locations' rows per year and flag (summed).
- **Breakdowns:** Year of first order, Completeness flag, Location
- **Filters:** Year of first order; Location
- **Time logic:** Customer is placed by first-order year (created_at, UTC). The second order must fall in the window (first order, first order + 12 calendar months]. The window is also cut at 2026-09-30.
- **Cleaning:** Apply all shared rules.; Second order must be a different order_id. Duplicate rows of the same order_id do not create a repeater.; Returned orders count as second orders. Cancelled orders do not.
- **Excluded example:** A customer whose second order came 13 months after the first is not a repeater. Nor is one whose only other order is Cancelled.

## 3. 12-month repeat rate

*What share of each year's first-time customers ordered again within 12 months, and where has it moved?*

- **Formula:** Repeat customers divided by first-time customers for the same group (first-order year x completeness flag x location). One-order customers stay in the base. For 'All locations' rows, divide the summed repeaters by the summed first-time customers.
- **Grain:** One row per first-order year x completeness flag x location, plus 'All locations' rows per year and flag. Columns: first-time customers, repeat customers, rate, small-group flag.
- **Breakdowns:** Year of first order, Completeness flag, Location (United States, each other country, Unknown)
- **Filters:** Year of first order; Location
- **Time logic:** Same as the two counts. Main view: complete customers only (first order 2019-01-01 to 2025-09-30), so 2025 here means Jan-Sep 2025. Separate section: first orders 2025-10-01 to 2026-09-30, labeled 'not yet complete: not final'. These rates only use time observed so far and are not like-for-like with complete groups. Readers are pointed to the 6-month repeat rate for a like-for-like view.
- **Cleaning:** Apply all shared rules.; If a group has no first-time customers, show the rate as blank ('no customers'), never 0%. Such rows are not charted.; Flag groups under 50 customers as small.
- **Excluded example:** A customer who first ordered on 2025-11-10 is not in the main view. They appear only in the 'not yet complete: not final' section.

## 4. 6-month repeat rate (same-time comparison)

*Using the same 6-month window for every first-order year, did the repeat rate really drop in recent groups such as 2026, and where?*

- **Formula:** Customers whose first-order year, flag and location match the row AND who have at least one other valid order (different order_id) with created_at strictly later than the first order's created_at and on or before first order created_at + 6 calendar months, divided by first-time customers in the same row. Use a calendar-month function (e.g. DATETIME_ADD(..., INTERVAL 6 MONTH)), not 180 days. One-order customers stay in the base. For 'All locations' rows, divide summed 6-month repeaters by summed first-time customers. Columns: first-time customers, 6-month repeat customers, 6-month rate, small-group flag.
- **Grain:** One row per first-order year x 6-month completeness flag x location, plus 'All locations' rows per year and flag (summed).
- **Breakdowns:** Year of first order, 6-month completeness flag (complete / not yet complete: not final), Location (United States, each other country, Unknown)
- **Filters:** Year of first order; Location
- **Time logic:** Customer is placed by first-order year (created_at, UTC). Second order must fall in (first order, first order + 6 calendar months], also cut at 2026-09-30. Main like-for-like view: first orders 2019-01-01 to 2026-03-31, so 2026 here means Jan-Mar 2026 only. Separate section: first orders 2026-04-01 to 2026-09-30, labeled 'not yet complete: not final' (these have under 6 months observed and will look lower).
- **Cleaning:** Apply all shared rules.; Second order must be a different order_id. Returned orders count as second orders. Cancelled orders do not.; If a group has no first-time customers, show the rate as blank ('no customers'), never 0%. Such rows are not charted.; Flag groups under 50 customers as small.
- **Excluded example:** A customer whose second order came 8 months after the first is not a 6-month repeater, though they count as a 12-month repeater. A customer who first ordered on 2026-05-15 is not in the main 6-month view.

## Confirmed with the stakeholder

- Should cancelled orders be ignored when finding a customer's first and second order? Returned orders would still count. Answer: Ignore cancelled orders and keep returned ones counted. That's the standard way to measure real purchases, so go with your suggestion.
- For the recent groups that do not have 12 months of history yet (Oct 2025 onward), how should the rate be shown? Answer: Go with the same-time comparison, such as the 6-month repeat rate for every year, along with the "not final" labels. I need to know whether 2026 really dropped, and without a like-for-like measure the recent groups will look worse just because they've had less time to reorder.

## Decisions assumed (please confirm)

- 'Within 12 months' = second order is later than the first and no later than first order + 12 calendar months (UTC timestamp). Edge dates such as 31 Jan follow the date function's rule consistently.
- 'Within 6 months' for the same-time comparison follows the same rule with 6 calendar months.
- The 6-month view is complete for first orders up to 2026-03-31. So 2026 in the like-for-like view covers January to March 2026 only. April to September 2026 is shown separately as not final.
- The 6-month rate is shown for every first-order year, 2019 to 2026, next to the 12-month rate.
- A same-day second order counts, if it is a different order_id with a strictly later timestamp.
- The 5 orders dated 2027 or 2028 are excluded and logged. Their true dates are unknown.
- Duplicate order_ids are collapsed to one row (earliest created_at if they differ).
- The 5 orders with bad item counts or bad delivery dates are kept. Neither field is used.
- 'España' is merged into 'Spain'. 'Brasil' stays as its only spelling.
- Customers with a missing user row or null country go into 'Unknown'. Their count is checked before launch.
- Location is the country on file, not necessarily where they lived at first order.
- 12-month complete = first order on or before 2025-09-30, set per customer. So 2025 is split: Jan-Sep complete, Oct-Dec not yet complete.
- 2026 is partial in the 12-month view and shown only in the not-yet-complete section. 'This year' = 2026 through 2026-09-30.
- 2019 may include customers who first ordered before 2019. It is shown with a caveat. 2020 onward is the cleaner baseline.
- Small-group flag threshold is 50 first-time customers.
- Empty groups (no customers) show a blank rate, not 0%.
- Customers who never ordered or only have cancelled orders are not in the base.
- Cause of any change and loyalty offer impact cannot be answered. The data has no offer or campaign records.
