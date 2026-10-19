# Metric Plan

**Time window:** 2025-10-01 to 2026-09-30. The 12 complete calendar months ending at the last day of data (30 Sep 2026). Items are placed in a month by order_items.created_at (UTC). Use created_at >= 2025-10-01 and < 2026-10-01, because order_items has rows dated into early October 2026 that must be left out.

**Rules applied to every metric:**

- Base table is order_items joined to products on order_items.product_id = products.id. One row is one item.
- Status comes from order_items.status, never from orders.status. 'Sold' means status in ('Complete','Returned'). 'Returned' means status = 'Returned'. Cancelled, Shipped and Processing are left out of both the top and the bottom of every rate.
- Month and period come from order_items.created_at (UTC), the order date. Do not use returned_at, delivered_at or shipped_at anywhere. Their timestamps are wrong for many rows.
- Exclude order items whose product_id is not in products.id (IDs 30001 to 30005) from every metric, including the company-wide reference. Log how many were excluded.
- Clean category before grouping: trim spaces and map 'JEANS' and 'jeans ' to 'Jeans', 'Tops and Tees' to 'Tops & Tees', 'Sweater' to 'Sweaters', 'Accesories' to 'Accessories'. Do not combine any other categories. Overlapping pairs (Socks and Socks & Hosiery, Pants and Pants & Capris, Suits and Suits & Sport Coats) stay separate, as in the data.
- Clean brand before grouping: trim spaces and ignore upper/lower case differences. Other spelling variants are not merged, and this is noted as a limit.
- Keep items with sale_price <= 0 (5 rows). Status decides if an item counts. No metric here uses price.
- Volume cut-off (confirmed): a category or brand is ranked only if its 12-month items sold is at least 300. The same 300 applies to categories and brands. Items from groups below the cut-off stay in the overall totals and the company-wide rate. They are shown as one 'Below cut-off' row, not listed one by one.
- Brands: rank the top 15 by return rate among brands that pass the cut-off. If fewer than 15 pass, show only those that pass. Ties go to more returned items, then to name A to Z. Categories: show every category that passes the cut-off.
- Items with a null brand are grouped as 'Unknown'. 'Unknown' is not ranked as a brand but stays in category totals and overall totals.
- Category and brand filters apply to the ranking tables, the KPIs and the trend. The company-wide reference line ignores the filters.
- No personal fields (name, email) appear anywhere.

## 1. Return rate (items)

*Which categories and brands have the highest share of items sent back, among those with enough volume?*

- **Formula:** Returned items divided by items sold. Numerator: count of order_items with status = 'Returned'. Denominator: count of order_items with status in ('Complete','Returned'). Shown as a percentage.
- **Grain:** Two small tables. One row per category that passes the cut-off. One row per brand in the top 15 that passes the cut-off. Each table has one extra 'Below cut-off' row. A card shows the overall rate for the 12 months.
- **Breakdowns:** Product category, Brand (top 15 by return rate, volume of 300 or more)
- **Filters:** Category; Brand; order_items.created_at >= 2025-10-01 and < 2026-10-01; status in ('Complete','Returned'); items sold in the 12 months >= 300 for ranked rows
- **Time logic:** 12-month total from 2025-10-01 to 2026-09-30. Each item is placed by order_items.created_at (order date), not by return date.
- **Cleaning:** If items sold is 0 (no denominator), the rate is blank and shown as 'no sales'. The group is not ranked.; Recent items have had less time to be returned. The rate for the latest months is probably understated. This is noted on the dashboard.
- **Excluded example:** A Cancelled item, or an item still Processing or Shipped, is not counted in the numerator or the denominator.

## 2. Items sold (volume)

*How many items sit behind each rate, and does the group pass the 300-item cut-off?*

- **Formula:** Count of order_items with status in ('Complete','Returned'). This is the same as the return rate denominator.
- **Grain:** One row per category and one row per brand (same rows as the return rate tables), plus a 'Below cut-off' row and a total.
- **Breakdowns:** Product category, Brand (top 15 by return rate, volume of 300 or more)
- **Filters:** Category; Brand; order_items.created_at >= 2025-10-01 and < 2026-10-01; status in ('Complete','Returned')
- **Time logic:** 12-month total from 2025-10-01 to 2026-09-30, placed by order_items.created_at. The cut-off is tested on the 12-month total, not on single months.
- **Cleaning:** A group with 0 items sold shows 0 and is counted in 'Below cut-off'.
- **Excluded example:** An item ordered on 2026-10-03 is left out because it falls after the window.

## 3. Returned items

*How many items were returned, so the size of the problem is clear next to the rate?*

- **Formula:** Count of order_items with status = 'Returned'.
- **Grain:** One row per category and one row per brand (same rows as the return rate tables), plus a 'Below cut-off' row and a total.
- **Breakdowns:** Product category, Brand (top 15 by return rate, volume of 300 or more)
- **Filters:** Category; Brand; order_items.created_at >= 2025-10-01 and < 2026-10-01; status = 'Returned'
- **Time logic:** 12-month total from 2025-10-01 to 2026-09-30, placed by order_items.created_at (order month). A return is counted in the month the item was ordered.
- **Cleaning:** Count a return from status only. 637 returned items have a return time earlier than the order time, so returned_at is not used.
- **Excluded example:** An item with status 'Complete' that may be returned later is not counted as returned.

## 4. Monthly return rate trend

*How has the return rate moved month by month, overall and for a chosen category or brand?*

- **Formula:** Same as Return rate (items), calculated for each order month: returned items divided by items sold in that month. Also shows returned items and items sold for the month. A company-wide rate line is shown as a reference for the same months.
- **Grain:** One row per order month (12 rows) for the overall rate, plus 12 rows for each selected category or brand.
- **Breakdowns:** Month (order month), Selected category or brand (optional)
- **Filters:** Category; Brand; order_items.created_at >= 2025-10-01 and < 2026-10-01; status in ('Complete','Returned')
- **Time logic:** Calendar month of order_items.created_at (UTC), from 2025-10 to 2026-09. All 12 months are shown.
- **Cleaning:** No monthly cut-off is applied. Show items sold next to each month so small counts are visible.; Mark Aug 2026 and Sep 2026 as 'incomplete: recent orders may still be returned'.; If a month has 0 items sold, leave the rate blank (do not show 0%).
- **Excluded example:** A return recorded in Nov 2025 for an item ordered in Sep 2025 is not in the window. Items are placed by order date.

## Confirmed with the stakeholder

- How many items should a brand or category need before it can be ranked? We expect very few of the 2,756 brands to reach 300 items in 12 months. Answer: 300 for both is fine. That's in line with what I said, and I'd rather see a short list of brands that really matter than a long list of noisy ones.
- Some categories overlap: Socks and Socks & Hosiery, Pants and Pants & Capris, Suits and Suits & Sport Coats. Should we combine each pair? Answer: Keep them separate as they are in the data for now. I don't want to guess at groupings before a supplier conversation, and I'll check with merchandising if one of them comes up as a candidate.

## Decisions assumed (please confirm)

- Items are assigned to a month by the order date (order_items.created_at), not the return date.
- Items still Processing or Shipped are left out, since their outcome is not known.
- Return rate is counted in items, not orders or money.
- The company-wide return rate is shown as a reference line on the trend and as a benchmark on the ranking. It uses all items in the window, including low-volume groups, and ignores filters.
- Where there is nothing to divide by (no items sold), the rate is blank and shown as 'no sales'. The group is not ranked.
- Null brands are grouped as 'Unknown' and are not ranked as a brand. They stay in totals.
- Order items whose product does not exist (5 rows) are excluded from every metric so all views add up.
- The trend shows the overall rate and the rate for any selected category or brand. Aug and Sep 2026 are marked incomplete because recent returns are still arriving. The rate for these months is likely understated.
- Brand stands in for supplier, because the data has no supplier field. No return reasons are available, so none are shown.
- Brand spelling variants beyond spaces and case are not merged.
