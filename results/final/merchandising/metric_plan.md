# Metric Plan

**Time window:** 2025-10-01 to 2026-09-30. The 12 complete calendar months ending at the data end (30 Sep 2026). An item is in the window if order_items.created_at is on or after 2025-10-01 00:00 and before 2026-10-01 00:00 (UTC). Items dated 1 to 4 Oct 2026 are left out.

**Rules applied to every metric:**

- Start from products and LEFT JOIN order_items, so products with no sales stay in the ranking. Put the window, status and price filters in the join condition, not in WHERE.
- Window: order_items.created_at >= 2025-10-01 and < 2026-10-01. No other date column is used. Do not use shipped_at, delivered_at or returned_at (their dates are unreliable and not needed).
- Status: use order_items.status, not orders.status. Leave out 'Cancelled' items. Shipped, Processing, Complete and Returned items all count. Returns are not subtracted.
- Category cleaning, done before any ranking: trim spaces and standardise case on products.category, then map 'JEANS' and 'jeans ' to 'Jeans', 'Tops and Tees' to 'Tops & Tees', 'Sweater' to 'Sweaters', 'Accesories' to 'Accessories'. After mapping, check that no category has only one product.
- Price cleaning: leave out order items with sale_price < 0 (looks like a refund or entry error). Also leave out items with sale_price = 0 until the stakeholder says otherwise. They are not counted as units or revenue.
- Orphan items: order items whose product_id is not in products (IDs 30001 to 30005) cannot be ranked or costed. They drop out through the join from products. Report their count in a data notes section.
- List the excluded rows (negative price, zero price, orphans) in a data notes section on the dashboard.
- Cost: use products.cost (USD, one current unit cost per product). Cost history is not in the data, so margin is an approximation if costs changed.
- Revenue is the sale_price actually paid, in USD, so discounts are already included.
- Categories with similar names (Socks and Socks & Hosiery, Pants and Pants & Capris, Suits and Suits & Sport Coats) are ranked separately, as listed.
- Do not show any customer personal data. Only product-level and category-level figures are used.
- The dashboard states that order items are cut off at 30 Sep 2026 and that the flag is a prompt for review, not a final decision.

## 1. Units sold

*How many units of each product were sold in the last 12 months?*

- **Formula:** For each product: count of order_items rows (one row = one unit) that pass the shared rules. Numerator: those rows. No denominator. Products with no qualifying rows get 0, not blank.
- **Grain:** One row per product (products.id), with category, name and SKU. The dashboard table is sorted by flag, then units sold lowest first, and shows the first 100 rows. The category filter narrows it further.
- **Breakdowns:** Category, Product (name, SKU)
- **Filters:** Category; Candidate flag (flagged only / all products)
- **Time logic:** Window 2025-10-01 to 2026-09-30, placed by order_items.created_at.
- **Cleaning:** Count order_items.id, not orders.; Items with status 'Cancelled', sale_price <= 0, or an unknown product_id are not counted.; Returned items still count.
- **Excluded example:** A cancelled item for a T-shirt ordered in March 2026 is not counted as a unit sold.

## 2. Margin %

*How much of the money actually paid is left after product cost, for each product?*

- **Formula:** For each product: (SUM(sale_price) - SUM(products.cost)) / SUM(sale_price), summed over the same items as Units sold. Sum first, then divide. Do not average per-item margins. Shown as a percentage. It can be negative when sale prices are below cost. If a product has no qualifying items, revenue is 0 and Margin % is blank (NULL), shown as 'No sales'. Blank is never treated as 0%.
- **Grain:** One row per product (products.id), in the same table as Units sold.
- **Breakdowns:** Category, Product (name, SKU)
- **Filters:** Category; Candidate flag (flagged only / all products)
- **Time logic:** Window 2025-10-01 to 2026-09-30, placed by order_items.created_at.
- **Cleaning:** Same items as Units sold.; Cost is counted once per unit sold (products.cost times units).; Zero and negative sale_price items are left out of both revenue and cost.
- **Excluded example:** An item sold at price -120 is left out of revenue and cost, so it cannot wipe out a slow product's margin.

## 3. Category unit-sales percentile rank

*Where does each product sit by units sold compared with the other products in its own category?*

- **Formula:** PERCENT_RANK() over all products in the same cleaned category, ordered by Units sold lowest first. Value runs from 0 (lowest) to 1 (highest). Tied products share the same rank, so all products tied at the cutoff fall in the bottom group. Bottom 10% means percent rank <= 0.10. Zero-sale products are included in the ranking. If a category has only one product, the rank is blank and the product is not placed in the bottom group.
- **Grain:** One row per product (products.id), in the same table as Units sold.
- **Breakdowns:** Category, Product (name, SKU)
- **Filters:** Category
- **Time logic:** Uses Units sold for the window 2025-10-01 to 2026-09-30.
- **Cleaning:** Clean category names before ranking.; Rank across the full category before any filter is applied, so filtering never changes ranks.
- **Excluded example:** A product mislabelled 'jeans ' is ranked inside Jeans, not as its own one-product category.

## 4. Discontinuation candidate flag

*Which products are in the bottom 10% of their category by units and also earn under 20% margin?*

- **Formula:** Flag = 1 when category percent rank <= 0.10 AND Margin % < 0.20 (strictly under, so exactly 20.0% is not flagged). Otherwise 0. Returns are not used. A product with no sales has blank margin, so it cannot pass the margin test. As confirmed by the stakeholder, it is not flagged. It gets the status 'No sales', shown separately from flagged candidates and still visible in the product table. The flag is a prompt for review, not a decision.
- **Grain:** One row per product (products.id), in the same table as Units sold.
- **Breakdowns:** Category, Product (name, SKU)
- **Filters:** Category; Candidate flag (flagged only / all products)
- **Time logic:** Uses Units sold and Margin % for the window 2025-10-01 to 2026-09-30.
- **Cleaning:** Clean category names first, so tiny misspelled categories do not flag products automatically.; Items with sale_price <= 0 are already left out.
- **Excluded example:** A product in the bottom 10% of its category with a 25% margin is not flagged. A product with exactly 20.0% margin is not flagged.

## 5. Number of candidates

*How many products are flagged, in total and in each category?*

- **Formula:** Count of products with flag = 1. Shown as one total, and as a count per category. Next to it, show the number of 'No sales' products per category as a separate count (not added to the flagged total). If a category has no flagged products, show 0.
- **Grain:** One row per category (about 25 rows), plus one total row. Columns: category, products in category, flagged products, no-sales products.
- **Breakdowns:** Category
- **Filters:** Category
- **Time logic:** Uses the flag for the window 2025-10-01 to 2026-09-30.
- **Cleaning:** Count distinct products.id.; Use cleaned category names.
- **Excluded example:** A product with 0 units in the window is not counted as a candidate. It is counted in the separate 'No sales' column.

## Confirmed with the stakeholder

- Products with no sales in the last 12 months have no margin, so the rule 'margin under 20%' cannot be applied to them. How should they be handled? Answer: Show them as "No sales," separate from the flagged list. They can't meet the margin condition, so they shouldn't be flagged automatically, but I still need to see them.

## Decisions assumed (please confirm)

- Cancelled items are left out of units sold and margin. Returned items stay in, because returns do not factor in.
- Zero-sale products are included in the category ranking, so they count as the lowest sellers.
- Recently launched products are included and shown as normal. The data has no launch date, so they cannot be marked reliably.
- Ties at the 10% cutoff: every product tied at the cutoff is in the bottom group. Because most products sell 0 or 1 units, the bottom group may be much larger than 10% of a category. Check the real counts before sharing.
- Margin is calculated per product over all its units, not as an average of per-order margins.
- A margin of exactly 20% is not flagged.
- Items with sale_price = 0 are left out for now, as proposed in the audit. If they are real free gifts, they can be counted as units at zero revenue. Items with a negative price stay out.
- Order items are cut off at 30 Sep 2026 even though some run to 4 Oct 2026, to match the brief's window.
- Divide-by-zero: percent rank is blank for a category with only one product, never 0.
- Overlapping category names are ranked separately, not merged.
- Margin uses today's product cost for all sales, because there is no cost history.
