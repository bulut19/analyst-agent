**Q1:** What does "stop selling" mean for you? In other words, what makes a product a bad one to keep? For example: (a) it sells very little, (b) it makes little profit (price minus cost), (c) it is often returned, or (d) a mix of these. Which fits best?

**A:** It's a mix: (d). A product is a discontinuation candidate if it's in the bottom 10% by units sold over the last 12 months and its margin is below 20%.

**Q2:** Your rule uses units sold and margin. Should returns also count? Pick one: (a) No, just those two measures. (b) Yes, don't count returned or cancelled items as sold, and compute margin on kept sales only. (c) Yes, show the return rate as an extra column, but don't use it in the rule.

**A:** Stick with option (a). The rule is just units sold and margin, so no returns adjustments.

**Q3:** Two quick things. Who will read this (for example: merchandising team, executives, buyers)? And how should the list be broken down or filtered: by category, brand, department, or something else?

**A:** It's for my merchandising team and buyers, to feed next season's buying plan. Please group the list by category, and show units sold, revenue, and margin for each product.

---

# Requirements Brief

**Business question:** Which products meet the discontinuation rule: bottom 10% by units sold over the last 12 months AND margin below 20%?

**Audience:** Merchandising team and buyers.

**Decision it supports:** Which products to drop from next season's buying plan.

## KPIs

| KPI | Definition |
|---|---|
| Units sold | Number of items sold for each product over the last 12 months. No adjustment for returns. Cancelled items treatment: see open assumptions. |
| Revenue | Sum of the sale price of the items sold for each product over the last 12 months. No adjustment for returns. |
| Margin % | (Revenue minus total product cost) divided by revenue, for each product over the last 12 months. Cost is the product cost per unit times units sold. No adjustment for returns. |
| Discontinuation candidate flag | A product is flagged if its units sold are in the bottom 10% of all products with sales in the period AND its margin % is below 20%. |

## Scope

- **Breakdowns:** Category (list is grouped by category), Product (one row per product)
- **Filters:** Category, Candidate flag (show candidates only or all products)
- **Time range:** Last 12 months, up to the latest data available (September 2026), so roughly October 2025 to September 2026.
- **Comparison:** None requested.

## Assumptions to approve

- Cancelled orders are excluded from units sold and revenue, since those items were never sold. Returns are NOT excluded, as requested.
- Margin % uses actual sale price (revenue) and product cost, not list retail price.
- The bottom 10% is ranked across all products that had at least one sale in the 12 months, not within each category.
- Products with zero sales in the period are excluded from the ranking, because we cannot tell if they were still on offer.
- Products sold for less than the full 12 months (new launches) are included on the same basis. Their low units may reflect a short time on sale. Approve or ask for an exclusion.
- 'Last 12 months' is the 12 full months to the end of the latest month in the data. If September 2026 is incomplete, use the 12 full months before it.
- Ties at the 10% cut-off are all included.

## Out of scope

- Return rate is not part of the rule and is not shown, as the stakeholder chose to leave returns out.
- Stock levels, supplier terms and future demand are not in the data, so the dashboard cannot say whether a candidate should actually be dropped. It only flags products that meet the rule.
