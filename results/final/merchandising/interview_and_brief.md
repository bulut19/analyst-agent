**Q1:** What does "stop selling" mean for you? In other words, what makes a product a bad one to keep? For example: (a) it sells very little, (b) it makes little profit (price minus cost), (c) it is often returned, or (d) a mix of these. Which one matters most?

**A:** A product is a discontinuation candidate if it's in the bottom 10% by units sold over the last 12 months and its margin is under 20%. Both conditions have to hold, so it's option (d), a mix. Returns don't factor in.

**Q2:** Should the "bottom 10% by units sold" be ranked across all products together, or within each category (for example, within Jeans, within Tops)?

**A:** Rank within each category. Accessories will always sell fewer units than jeans or tops, so a company-wide cutoff would flag whole categories instead of the weak products in each one.

**Q3:** How should we calculate margin? (a) Based on list price: (retail price − cost) ÷ retail price. (b) Based on what customers actually paid in the last 12 months: (sale price − cost) ÷ sale price, across all units sold. Which do you prefer?

**A:** I'd go with (b). Discounts are a big part of how we sell, so margin on what customers actually paid is the number that shows whether a product really makes money.

**Q4:** Two last things. Who will read this dashboard (for example: merchandising team, executives)? And besides category, do you want to slice it by anything else, such as brand or department?

**A:** The merchandising team, mainly me and my buyers. Category is enough for the slicing, so skip brand and department.

---

# Requirements Brief

**Business question:** Which products are weak sellers, meaning low units sold within their category and low margin on actual sale prices, over the last 12 months?

**Audience:** Merchandising team (the head of merchandising and the buyers).

**Decision it supports:** Which products to review for discontinuation (stop selling).

## KPIs

| KPI | Definition |
|---|---|
| Units sold | Number of units of the product sold in the last 12 months. Cancelled orders are excluded (assumed). Returns are not subtracted, as the stakeholder said returns do not factor in. |
| Margin % | (Total revenue actually paid for the product's units in the last 12 months minus total cost of those units) divided by total revenue actually paid. Uses the real sale price, so discounts are included. |
| Category unit-sales percentile rank | The product's position by units sold among all products in the same category, over the last 12 months. Bottom 10% means the lowest 10% in that category. |
| Discontinuation candidate flag | A product is flagged only if both are true: it is in the bottom 10% by units sold within its category, and its margin % is under 20%. Returns are not considered. |
| Number of candidates | Count of flagged products, in total and per category. |

## Scope

- **Breakdowns:** Category, Product (list of individual products with units sold, margin %, and flag)
- **Filters:** Category, Candidate flag (flagged only / all products)
- **Time range:** Last 12 months, rolling, counted back from the latest date in the data (September 2026).
- **Comparison:** None. This is a snapshot of the last 12 months.

## Assumptions to approve

- Cancelled orders are excluded from units sold and from margin. Please confirm. The stakeholder said returns are ignored, but did not mention cancellations.
- Products with zero units sold in the last 12 months are included in the ranking, so they count as the lowest sellers. Please confirm.
- Products that launched recently (less than 12 months ago) have had less time to sell and may be unfairly flagged. Assumed they are included and shown as normal. Please say if you want them excluded or marked.
- Ties at the 10% cutoff: all products tied at the cutoff value are included in the bottom group (assumed).
- Margin is calculated per product across all units sold in the period, not per order. It is not an average of per-order margins (assumed).
- Margin of exactly 20% is not flagged, because the rule says under 20% (assumed).
- The flag is a prompt for review, not a final decision.

## Out of scope

- Return rates and return-based criteria are excluded because the stakeholder said returns do not factor in.
- Breakdowns by brand and department are not requested, so they are not included.
- Stock levels, supplier terms, and seasonality are not in the data described, so they cannot be used to judge whether a product should be dropped.
