# Metric Plan

**Time window:** 2025-10-01 to 2026-09-30. The last 12 complete calendar months ending at the data end (2026-09-30): October 2025 to September 2026. The order data runs to 2026-09-30, so September 2026 looks complete. This differs from the brief, which assumed September was partial and excluded it (see decisions_assumed). Items are placed in a month by order_items.created_at (UTC). Items created after 2026-09-30 are left out.

**Rules applied to every metric:**

- Base table is order_items (one row per item), joined to products on order_items.product_id = products.id. This is the only join. Item status is used, never orders.status.
- Window: order_items.created_at from 2025-10-01 00:00 UTC to 2026-09-30 23:59:59 UTC. Months are UTC calendar months of created_at.
- Items sold = items with status 'Complete' or 'Returned'. Returned = items with status 'Returned'. Cancelled, Shipped and Processing items are left out of both the top and the bottom of every rate.
- Do not use shipped_at, delivered_at or returned_at for any KPI or month placement. They are unreliable (ship dates before order dates on about 34,000 items, delivery dates before order dates on about 5,800, return dates before order dates on 637). Status decides delivered or returned. Do not drop these rows.
- Clean products.category: trim spaces and ignore case, then map JEANS and 'jeans ' to Jeans, 'Tops and Tees' to 'Tops & Tees', Sweater to Sweaters, Accesories to Accessories.
- Exclude order items whose product_id is not in products.id (IDs 30001 to 30005) from every KPI, including the company-wide rate, so all numbers use the same base. Show the count excluded in a footnote.
- Exclude order items with sale_price <= 0 from every KPI, including the company-wide rate. Show the count excluded in a footnote.
- Company-wide item return rate = returned items / items sold across ALL cleaned items in the window. No category, brand or minimum-volume filter is applied. It is a fixed benchmark and does not change when the user changes filters.
- Minimum volume filter (default on): keep a category or brand only if its items sold across the whole 12-month window is 100 or more. Evaluated separately for category and for brand. It is never applied month by month. It hides rows from the view only. It does not change the company-wide rate.
- Category and brand are shown separately. There is no category-by-brand view.
- Rates are stored as full-precision ratios and shown as percentages with 1 decimal. Gaps are shown in percentage points with 1 decimal. If a denominator is 0, the rate is blank, not 0.
- Ranking limits keep tables small: brands show the top 15 by gap to company average. Categories show all that pass the minimum volume.
- Return status is the current status, not a historical one. Recent months can still change as more returns come in.
- No personal data (names, emails) is used or shown.

## 1. Item return rate

*What share of delivered or returned items came back, for each category and each brand, over the last 12 months?*

- **Formula:** Numerator: count of order_items with status 'Returned'. Denominator: count of order_items with status in ('Complete','Returned'). Rate = numerator / denominator, per category or per brand.
- **Grain:** One row per category (all that pass the minimum volume) in one table, and one row per brand (top 15 by gap to company average, among brands that pass the minimum volume) in another.
- **Breakdowns:** products.category (cleaned), products.brand
- **Filters:** Window 2025-10-01 to 2026-09-30; Minimum volume: items sold >= 100 in the window (default on); Optional user filters: category, brand
- **Time logic:** Items are placed in the window by order_items.created_at (UTC), from 2025-10-01 to 2026-09-30 inclusive. One rate for the whole window, not per month.
- **Cleaning:** Brand is null on about 0.1% of products: label as 'Unknown'. 'Unknown' counts in the company-wide rate but is not ranked as a brand.; Category names that look alike ('Socks' and 'Socks & Hosiery', 'Pants' and 'Pants & Capris', 'Suits' and 'Suits & Sport Coats') are kept as separate values and not merged.
- **Excluded example:** An item with status 'Cancelled' (or still 'Shipped' or 'Processing') is not in the numerator or the denominator. So is a brand with only 80 delivered or returned items in the window.

## 2. Items returned

*How many items came back, for each category and brand, over the last 12 months?*

- **Formula:** Count of order_items with status = 'Returned'.
- **Grain:** One row per category (all that pass the minimum volume), and one row per brand (top 15 by gap to company average, among brands that pass the minimum volume). Shown next to the rate.
- **Breakdowns:** products.category (cleaned), products.brand
- **Filters:** Window 2025-10-01 to 2026-09-30; Minimum volume: items sold >= 100 in the window (default on); Optional user filters: category, brand
- **Time logic:** Placed in the window by order_items.created_at (UTC), the order date, not the return date. A return shows in the month the item was ordered.
- **Cleaning:** Count from status only. Do not use returned_at.
- **Excluded example:** An item ordered in September 2025 and returned in November 2025 is not counted, because its order date is before the window.

## 3. Items sold (delivered or returned)

*How many items were delivered or returned, for each category and brand? This is the volume behind each rate.*

- **Formula:** Count of order_items with status in ('Complete','Returned').
- **Grain:** One row per category (all that pass the minimum volume), and one row per brand (top 15 by gap to company average, among brands that pass the minimum volume). Shown next to the rate. Also used for the 100-item minimum.
- **Breakdowns:** products.category (cleaned), products.brand
- **Filters:** Window 2025-10-01 to 2026-09-30; Minimum volume: items sold >= 100 in the window (default on); Optional user filters: category, brand
- **Time logic:** Placed in the window by order_items.created_at (UTC). Delivery date is not used.
- **Cleaning:** Count from status only. Do not use delivered_at.
- **Excluded example:** An item with status 'Processing' is not counted, because it has not been delivered, returned or cancelled.

## 4. Gap to company average

*How far above or below the company-wide return rate is each category or brand? This is how 'unusually high' is ranked.*

- **Formula:** (Item return rate of the category or brand) minus (company-wide item return rate), both for 2025-10-01 to 2026-09-30, in percentage points. Positive means worse than average. Rows are ranked from highest gap to lowest.
- **Grain:** One row per category (all that pass the minimum volume) and one row per brand (top 15 by gap, among brands that pass the minimum volume). One extra card shows the company-wide rate.
- **Breakdowns:** products.category (cleaned), products.brand
- **Filters:** Window 2025-10-01 to 2026-09-30; Minimum volume: items sold >= 100 in the window (default on); Optional user filters: category, brand. They do not change the company-wide rate.
- **Time logic:** Both the group rate and the company rate use order_items.created_at (UTC) from 2025-10-01 to 2026-09-30 inclusive.
- **Cleaning:** Company-wide rate uses all cleaned items, with no category, brand or volume filter.; No fixed cut-off for 'unusually high' is applied. Ranking only.
- **Excluded example:** A brand with 60 items sold in the window is left out of the ranking by the minimum volume filter. Its items still count in the company-wide rate.

## 5. Monthly item return rate

*Is the return rate for a category or brand rising month by month over the last 12 months?*

- **Formula:** For each month: returned items / items sold (status 'Complete' or 'Returned') for that category or brand, items placed by created_at month. Show items sold for the month beside the rate. Also show the company-wide monthly rate as a reference line. The latest two months (August and September 2026) are flagged as 'immature'. They are kept, but shown as likely understated.
- **Grain:** One row per month (12 months, Oct 2025 to Sep 2026) per category or brand. Categories: top 10 by gap to company average among those passing the minimum volume. Brands: top 15 by gap to company average. One extra 'Company' row per month.
- **Breakdowns:** Month (UTC calendar month of order_items.created_at), products.category (cleaned), products.brand
- **Filters:** Window 2025-10-01 to 2026-09-30; Only categories and brands that pass the 100-item minimum across the 12 months (default on). The threshold is not applied per month.; Optional user filters: category, brand
- **Time logic:** Month = UTC calendar month of order_items.created_at. The order date places the item, not the return date. Months: 2025-10, 2025-11, 2025-12, 2026-01 to 2026-09.
- **Cleaning:** A month with 0 items sold shows a blank rate.; Recent months are biased downward because recent items have had less time to be returned and some are still Shipped or Processing. Flag August and September 2026.; The rule for 'worse' is not fixed. Show the monthly line with monthly volume, so small months can be judged.
- **Excluded example:** A brand with 150 items sold in the 12 months but only 4 in March 2026 still appears, but its March point is based on 4 items. A brand with 90 items over 12 months does not appear at all.

## Decisions assumed (please confirm)

- Time window: 2025-10-01 to 2026-09-30 (Oct 2025 to Sep 2026). The brief assumed September 2026 is partial and excluded. The order data runs to 2026-09-30, so September looks complete. If you prefer to exclude September, the window becomes Sep 2025 to Aug 2026.
- Month placement: every item is placed by order date (created_at). Ship date and return date are unreliable. The trade-off is that a return shows in the month of the order, not the month the customer sent it back.
- Items still Shipped or Processing are left out of both the top and bottom of the rate.
- 'Unusually high' = ranked by gap to company average, with the 100-item minimum. No fixed cut-off such as +5 points is set. Please say if you want one.
- 'Getting worse' has no fixed rule. The dashboard shows the monthly rate with monthly volume and flags Aug and Sep 2026 as immature. A 3-month rolling rate could be added if you want it.
- Minimum volume of 100 is applied to the 12-month total only, and the trend shows only categories and brands that pass it.
- Company-wide benchmark uses all cleaned items, ignoring filters and the 100-item minimum.
- Category names that look alike (Socks / Socks & Hosiery, Pants / Pants & Capris, Suits / Suits & Sport Coats) are kept separate, not merged. A merged one could pass the 100 minimum when the separate ones do not. Please say if you want them merged.
- Brands with no name are labelled 'Unknown'. They count in the company rate but are not ranked as a brand.
- Brand is treated as the supplier. Brands owned by the same supplier cannot be grouped.
- Result size: brands show the top 15 by gap, the category trend shows the top 10 by gap, and category tables show all categories that pass the minimum.
- Items with an unknown product_id (5 items) and items with sale_price <= 0 (5 items) are excluded from every number, including the company rate. Counts are shown in a footnote.
- Category and brand are shown separately, with no combined view.
