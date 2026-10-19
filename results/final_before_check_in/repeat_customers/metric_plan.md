# Metric Plan

**Time window:** 2019-01-01 to 2026-09-30. Customer groups are set by the year of first order, 2019 to 2025. Only first orders placed 1 January to 30 September count in every year, so each group gets a full 365 days of follow-up and all years are compared on the same months. The last first order (30 Sep 2025) is followed to 30 Sep 2026, the last day of order data. The data starts on 2019-01-13, so the 2019 group begins then. 2026 first-order groups are not shown.

**Rules applied to every metric:**

- Order table cleaning, in this order: (1) if an order_id appears more than once, keep one row. If the copies are identical, keep one. If they differ, keep the earliest-created row and log the rest. (2) Drop orders with no user_id. (3) Drop orders with created_at after 2026-09-30 (the 2027 and 2028 dates). (4) Drop orders with status 'Cancelled'. Log every dropped row count.
- Orders that count: status is Complete, Returned, Shipped or Processing. Returned orders count as orders. Cancelled orders never count, including as a first order.
- A customer's first order is their earliest counted order by orders.created_at (UTC). Ties are broken by the lowest order_id. If the true first order was cancelled, the next counted order becomes the first.
- A customer's second order is the next counted order after the first, by created_at then order_id. Several items in one order are one order. Count distinct order_id, never item rows.
- Cohort year = calendar year (UTC) of the first order's created_at. Only first orders from 1 Jan to 30 Sep of that year are included, in every year from 2019 to 2025. First orders from October to December are left out.
- 12-month window = 365 days. A customer is a repeat buyer if the second order's created_at is on or before the first order's created_at plus 365 days. A second order on the same day counts (0 days).
- Always count distinct user_id. After joining orders to order_items and products, never count rows.
- Customer attributes (channel, gender, age, country, state) come from the users table as currently recorded, not as at the first order. Label this on the dashboard. Orders with no matching users row stay in the totals and show as 'Unknown' in the customer breakdowns.
- Gender is the customer's gender from users.gender. It is not the product department. Keep the two views separate.
- Country cleaning: merge 'España' into 'Spain'. Keep 'Brasil' and 'Brazil' as one country (Brazil). Trim spaces before grouping.
- Category cleaning: trim spaces and ignore case. Map 'Tops and Tees' to 'Tops & Tees', 'Sweater' to 'Sweaters', 'Accesories' to 'Accessories', and 'JEANS' and 'jeans ' to 'Jeans'. Other similar names (Socks and Socks & Hosiery, Pants and Pants & Capris, Suits and Suits & Sport Coats) are left as separate groups.
- First-order items for category, department and brand views: use the actual order_items rows of the first order, ignoring items with item status 'Cancelled'. Do not use orders.num_of_item. Orders with num_of_item above 40 are checked against their real item row count and kept only if they match. Otherwise they stay in the repeat counts but are left out of category, department and brand views.
- Items whose product_id has no product row (30001 to 30005) show as 'Unknown product' in category, department and brand views. Their orders stay in all counts. A first order with no non-cancelled items shows as 'No active items'.
- In category, department and brand views, a customer is counted in every group their first order touches. Rates and counts in these views do not add up to the total. Always take totals from the view with no breakdown.
- Show the new-customer count beside every rate. Hide the rate (show 'too few') where the group has fewer than 100 new customers in that year.
- Do not use sale_price, delivered_at, shipped_at or returned_at. Do not show first_name, last_name or email.
- Use one breakdown at a time. Do not cross two breakdowns in one table.

## 1. New customers (count)

*How many new customers did we win in January to September of each year? This is the base for the repeat rate.*

- **Formula:** Count of distinct user_id whose first counted order falls in the cohort year (1 Jan to 30 Sep). No denominator.
- **Grain:** One row per first-order year (2019 to 2025). With a breakdown: one row per first-order year per breakdown value.
- **Breakdowns:** Marketing channel (users.traffic_source), Product category of first order, Department of first order (Men, Women), Brand of first order: top 15 by pooled new customers across 2019 to 2025, rest as 'Other', null as 'Unknown', Customer gender (F, M), Age band: Under 18, 18-24, 25-34, 35-44, 45-54, 55+, Country (cleaned): top 10 by pooled new customers, rest as 'Other'. State drill-down: top 15 within one chosen country.
- **Filters:** First-order year 2019 to 2025; Marketing channel; Product category; Department; Gender; Age band; Country and state
- **Time logic:** A customer is placed in a year by the created_at (UTC) of their first counted order. First order must be on or after YYYY-01-01 and before YYYY-10-01. For 2019, data starts 2019-01-13. Orders are counted up to 2026-09-30.
- **Cleaning:** Apply all shared order cleaning rules.; Category, department, brand views: use first-order items only and the shared item rules.; Customers with no users row show as 'Unknown'.
- **Excluded example:** A customer whose first counted order was placed on 14 November 2025. It is outside January to September, so they are not in the 2025 group. Also excluded: a customer whose only order was cancelled.

## 2. Repeat buyers (count)

*How many new customers placed a second order within 12 months of their first order? When did that second order come?*

- **Formula:** Count of distinct user_id in the cohort whose second counted order has created_at on or before first order created_at + 365 days.
- **Grain:** One row per first-order year. With a breakdown: one row per first-order year per breakdown value. For the timing view: one row per first-order year per days-between bucket.
- **Breakdowns:** Marketing channel (users.traffic_source), Product category of first order, Department of first order, Brand of first order: top 15 by pooled new customers, rest as 'Other', Customer gender, Age band: Under 18, 18-24, 25-34, 35-44, 45-54, 55+, Country (cleaned): top 10, rest 'Other'. State drill-down: top 15 within one chosen country., Time between first and second order, in whole days (rounded down), in buckets: 0, 1-7, 8-30, 31-60, 61-90, 91-180, 181-270, 271-365
- **Filters:** First-order year 2019 to 2025; Marketing channel; Product category; Department; Gender; Age band; Country and state
- **Time logic:** Customer is placed in a year by the first order's created_at (1 Jan to 30 Sep). The second order must have created_at no later than first created_at + 365 days. The latest possible follow-up end is 2026-09-30.
- **Cleaning:** Apply all shared order cleaning rules.; Days between = floor of (second created_at minus first created_at) in days, UTC timestamps.; Timing view shows only repeat buyers inside the 365-day window, so it adds up to the repeat buyer count.
- **Excluded example:** A customer whose second order was placed 400 days after their first. They are not a repeat buyer. Also excluded: a customer whose second order was cancelled, or whose second 'order' is a duplicate row of the first order_id.

## 3. 12-month repeat buyer rate

*Did the share of new customers who buy again within 12 months fall for the 2025 group compared with 2024 and earlier groups? Where is the drop?*

- **Formula:** Repeat buyers (count) divided by New customers (count), for the same year and breakdown value. Shown as a percent with one decimal. Calculated from the two counts, never by averaging customer-level or group-level rates.
- **Grain:** One row per first-order year (2019 to 2025). With a breakdown: one row per first-order year per breakdown value, with the new-customer count beside the rate.
- **Breakdowns:** Marketing channel (users.traffic_source), Product category of first order, Department of first order, Brand of first order: top 15 by pooled new customers, rest as 'Other', Customer gender, Age band: Under 18, 18-24, 25-34, 35-44, 45-54, 55+, Country (cleaned): top 10, rest 'Other'. State drill-down: top 15 within one chosen country.
- **Filters:** First-order year 2019 to 2025; Marketing channel; Product category; Department; Gender; Age band; Country and state
- **Time logic:** Same as the two counts: first-order year from the first order's created_at (1 Jan to 30 Sep), 365-day follow-up, data to 2026-09-30.
- **Cleaning:** Apply all shared order cleaning rules.; Hide the rate where new customers are fewer than 100 in that year and group.; With a filter, the denominator is the filtered new-customer count.
- **Excluded example:** A customer who joined in 2025 but whose first counted order was in October 2025. They have under 12 months of follow-up, so they are in neither the numerator nor the denominator.

## 4. Change in repeat rate vs prior groups

*By how many percentage points is the 2025 repeat rate above or below the 2024 group and the earlier 2019 to 2023 groups?*

- **Formula:** Two differences in percentage points: (a) 2025 rate minus 2024 rate; (b) 2025 rate minus the pooled 2019-2023 rate, where pooled = all repeat buyers in 2019-2023 divided by all new customers in 2019-2023. Both use the 12-month repeat buyer rate defined above.
- **Grain:** One row per comparison (2025 vs 2024, 2025 vs 2019-2023 pooled). With a breakdown: one row per breakdown value per comparison, showing 2025 rate, comparison rate, difference and both customer counts.
- **Breakdowns:** Marketing channel (users.traffic_source), Product category of first order, Department of first order, Brand of first order: top 15 by pooled new customers, rest as 'Other', Customer gender, Age band: Under 18, 18-24, 25-34, 35-44, 45-54, 55+, Country (cleaned): top 10, rest 'Other'
- **Filters:** Marketing channel; Product category; Department; Gender; Age band; Country and state
- **Time logic:** Uses the yearly rates: 2025 group (first orders 2025-01-01 to 2025-09-30), 2024 group (2024-01-01 to 2024-09-30), and 2019-2023 groups (first orders 1 Jan to 30 Sep of each year, 2019 starting 2019-01-13). Follow-up 365 days from each first order.
- **Cleaning:** Apply all shared order cleaning rules.; Show the difference only if both groups have at least 100 new customers.; Sort breakdown rows by the size of the drop (most negative first) so the biggest drivers show first.
- **Excluded example:** The 2026 first-order group, and the 2025 October to December first orders. Neither is in either side of the comparison.

## Decisions assumed (please confirm)

- Cohort window: for every year 2019 to 2025, only first orders from 1 January to 30 September are included. 2025 is not shown as partial. Overrule if you want full-year groups.
- 'This year' means the 2025 first-order group. 2026 groups are not shown.
- The 12-month window is 365 days from the first order's timestamp, not calendar months.
- First order = earliest non-cancelled order. If the first order was cancelled, the next non-cancelled order is the first.
- Comparison with earlier groups uses the pooled rate for 2019-2023 (all repeat buyers / all new customers). The other option is a simple average of the five yearly rates.
- Age bands: Under 18, 18-24, 25-34, 35-44, 45-54, 55+. Based on current age, not age at first order.
- Customers in category, department and brand views are counted in every group their first order touches, so totals will not add up.
- Items with item status 'Cancelled' are ignored in category, department and brand views.
- Brand view shows the top 15 brands by pooled new customers (2019 to 2025). The rest are 'Other'. Country view shows the top 10 countries. State drill-down shows the top 15 states in one chosen country.
- Minimum group size: rates and differences are hidden where there are fewer than 100 new customers in a year. Overrule to change the number.
- Similar category names (Socks / Socks & Hosiery, Pants / Pants & Capris, Suits / Suits & Sport Coats) are not merged. Only the spelling fixes are applied.
- Orders dated after 2026-09-30, orders with no customer, and duplicate order IDs are removed as per the audit. The counts removed will be reported.
- Orders with num_of_item above 40 stay in the repeat counts but are left out of category, department and brand views if the item count does not match the real item rows.
- Customers with no matching users row are shown as 'Unknown' in customer breakdowns and stay in totals.
- Time between orders is shown in whole days (rounded down) in buckets, for second orders inside 365 days only.
- Gender means the customer's gender, not the department of the product bought.
- Channel is the sign-up channel, one value per customer. It may not be what led to the first purchase.
- The 2019 group may be thin and may include customers who bought before the data starts. Read 2019 with care.
- Price and discount are not used. Reasons customers did not return cannot be shown, only where the drop is concentrated.
