# Metric Plan

**Time window:** 2025-10-01 to 2026-09-30. The 12 complete calendar months ending at the data end (Oct 2025 to Sep 2026). Items are placed in the window by order_items.created_at (UTC): created_at >= 2025-10-01 and < 2026-10-01. The upper limit also removes a few stray items dated 1 to 4 Oct 2026.

**Rules applied to every metric:**

- Source table is order_items, joined to products on order_items.product_id = products.id. Do not join orders or users.
- One row in order_items is one item. Count items with COUNT(order_items.id). Each item is counted once.
- Use order_items.status only. Do not use orders.status.
- Status values: 'Returned' = returned. 'Complete' = delivered and kept. There is no 'Delivered' status, so 'Complete' plus 'Returned' stands in for 'delivered or returned'.
- Cancelled, Shipped and Processing items are left out of every count and every rate, including the company-wide benchmark.
- Place every item in a period by order_items.created_at (the order date), in UTC. Never use returned_at, shipped_at, delivered_at or orders.created_at.
- Clean products.category before grouping or filtering: trim spaces, ignore upper/lower case, then map JEANS and 'jeans ' to 'Jeans'; 'Tops and Tees' to 'Tops & Tees'; 'Sweater' to 'Sweaters'; 'Accesories' to 'Accessories'. After mapping, check that no rare category variants remain.
- Exclude order items whose product_id does not exist in products (5 items, IDs 30001 to 30005). Exclude them from every view, including the company-wide benchmark, so totals match. Log the count.
- Do not drop rows because of impossible timestamps (return before order, shipping or delivery before order). The KPIs use status and created_at only.
- sale_price is not used. Rows with sale_price <= 0 stay in the item counts.
- Minimum volume: a category or a brand is shown only if its items sold (Complete + Returned) over the 12-month window is at least 500. The cut-off is applied separately to categories and to brands, never to brand within category, and never per month.
- The company-wide benchmark has no 500-item cut-off. It includes items from small categories and brands, and items with a null brand.
- Brand and category are not nested. A brand's rate covers all its categories. A category's rate covers all its brands.
- Filters (category, brand, department) apply to every view. Department uses products.department, not customer gender. The 500-item cut-off is applied after the filters.
- Show rates as a percentage with one decimal place. If the rate base is 0, show no value (null), not 0%.
- No personal data (names, email) appears anywhere. Result tables are small aggregates, never raw rows.

## 1. Return rate

*Which categories and brands have the highest share of items coming back, and how is that share changing month by month?*

- **Formula:** Items returned ÷ items sold, where items returned = count of items with status 'Returned', and items sold = count of items with status 'Complete' or 'Returned'. Calculated within each group (category, brand or month), never from the 12-month total. Benchmark: the same formula across all items in the 12-month window with no category or brand grouping and no 500-item cut-off, shown as a reference line against each category, brand and month. The benchmark responds to the Department filter only.
- **Grain:** Three small result tables. (1) Category view: one row per category. (2) Brand view: one row per brand. (3) Trend: one row per calendar month (12 rows). Each row has the rate, items returned, items sold and the benchmark rate.
- **Breakdowns:** Product category (cleaned), Brand, Month of order date (created_at, UTC)
- **Filters:** Status in ('Complete','Returned') only; created_at >= 2025-10-01 and < 2026-10-01; Category and brand views: items sold >= 500 over the 12 months, applied separately to categories and to brands; Brand view: brand is not null; Optional filters: product category, brand, department (Men or Women)
- **Time logic:** Window: 2025-10-01 to 2026-09-30 inclusive, by order_items.created_at (UTC). Month = calendar month of created_at, so the trend runs Oct 2025, Nov 2025 ... Sep 2026. The rate for each month divides within that month. The 500-item cut-off is decided on the 12-month total and is not applied per month.
- **Cleaning:** Category view and brand view: rank by return rate, highest first. Break ties by items sold, highest first.; Category view: show the top 15 categories by return rate among those that pass the cut-off.; Brand view: show the top 15 brands by return rate among those that pass the cut-off. There are about 2,700 brands, so a limit is needed.; Brand view: items with a null brand (about 0.1% of products) are left out. They stay in category views, the trend and the benchmark.; Category names are used as they appear after cleaning. Look-alike names ('Socks' and 'Socks & Hosiery', 'Pants' and 'Pants & Capris', 'Suits' and 'Suits & Sport Coats') are NOT merged.; Read the latest 2 to 3 months with care. Status is the current status, and recent items may still be returned later, so recent rates are probably understated.
- **Excluded example:** An item with status 'Cancelled' (or 'Shipped' or 'Processing') is left out of both the returned count and the sold count. So is an item from a brand with only 300 delivered or returned items in the 12 months: it is left out of the brand view, but still counts in the benchmark.

## 2. Items returned

*How many items came back, for each category, brand and month?*

- **Formula:** Count of order items with status = 'Returned'. Cancelled, Shipped, Processing and Complete items are not counted. Each item is counted once.
- **Grain:** Shown next to the return rate in the same tables: one row per category, one row per brand, and one row per calendar month.
- **Breakdowns:** Product category (cleaned), Brand, Month of order date (created_at, UTC)
- **Filters:** status = 'Returned'; created_at >= 2025-10-01 and < 2026-10-01; Category and brand views: only groups that pass the 500 items sold cut-off; Brand view: brand is not null; Optional filters: product category, brand, department
- **Time logic:** Window: 2025-10-01 to 2026-09-30 inclusive. An item is placed in a month by order_items.created_at (order date), not by returned_at.
- **Cleaning:** Define 'returned' by status only. Do not use returned_at, because 637 items have a return time before the order time.; Use the same top 15 ranking as the Return rate metric for the category and brand views.
- **Excluded example:** An item with status 'Cancelled' is not counted as returned, even if it has a returned_at value.

## 3. Items sold (return-rate base)

*How many items were delivered or returned? This is the base of the return rate and the volume used for the 500-item cut-off.*

- **Formula:** Count of order items with status 'Complete' or 'Returned'. Cancelled, Shipped and Processing items are not counted. Each item is counted once.
- **Grain:** Shown next to the return rate in the same tables: one row per category, one row per brand, and one row per calendar month.
- **Breakdowns:** Product category (cleaned), Brand, Month of order date (created_at, UTC)
- **Filters:** status in ('Complete','Returned'); created_at >= 2025-10-01 and < 2026-10-01; Category and brand views: items sold >= 500 over the 12-month window; Brand view: brand is not null; Optional filters: product category, brand, department
- **Time logic:** Window: 2025-10-01 to 2026-09-30 inclusive, by order_items.created_at (UTC). The 500-item cut-off uses the 12-month total for each category or brand, not each month.
- **Cleaning:** Do not use delivered_at to find delivered items. It is blank on about 65% of rows and often earlier than the order date. Use status.; Use the same top 15 ranking as the Return rate metric for the category and brand views.
- **Excluded example:** An item with status 'Processing' (ordered but not yet shipped) is left out, because it is neither delivered nor returned yet.

## Decisions assumed (please confirm)

- Window: Oct 2025 to Sep 2026 (2025-10-01 to 2026-09-30), using Sep 2026 as a full month. This follows the '12 complete months ending at the data end' rule. If you prefer to end at Aug 2026, the window becomes Sep 2025 to Aug 2026.
- Month is set by order date (created_at), not return date. The return-date alternative would answer when returns happen, and it would need a different base.
- The 500-item cut-off applies separately to categories and to brands (not brand within category). It uses items sold over the 12 months. It is not applied per month or to the benchmark.
- Items still Processing or Shipped are excluded from both parts of the rate.
- 'Delivered' is approximated by status 'Complete' plus 'Returned', because the data has no 'Delivered' status.
- Look-alike category names (Socks / Socks & Hosiery, Pants / Pants & Capris, Suits / Suits & Sport Coats) are kept separate and not merged. Merging would be a guess. Tell me if you want them merged. Either could be under the 500 cut-off on its own.
- Supplier is not in the data. Brand is used as a stand-in. The buying team must match brands to suppliers.
- Brand view shows the top 15 brands by return rate, and category view shows the top 15 categories by return rate, after the 500 cut-off. Change the limit if you want more.
- Items with a null brand are left out of the brand view only. They stay in the category views, the trend and the benchmark.
- The company-wide benchmark responds to the Department filter only. It does not change with the category or brand filter.
- Department filter is included as an optional filter, and it uses the product's department, not the customer's gender.
- The 5 items whose product does not exist in products are excluded everywhere, so the totals match. The data owner should be asked whether those products were deleted.
- Category typos (JEANS, 'jeans ', Tops and Tees, Sweater, Accesories) are corrected before grouping.
- The audience is assumed to be you plus the merchandising or buying team who run supplier reviews.
- Recent months are probably understated, because items ordered recently may still be returned. The dashboard will carry a note about this.
