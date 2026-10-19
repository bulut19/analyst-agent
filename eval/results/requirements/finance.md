# Interview: finance

**Request:** I need a revenue dashboard for the board.

**Hidden need (what the simulator knew):** You want monthly revenue and gross margin for 2025 and 2026 so far, compared year over year, split by department (Men and Women). Revenue means the sale price of items that were not cancelled or returned. Gross margin means revenue minus product cost, as a percentage of revenue. The board meets quarterly, so quarterly totals are also helpful.

## Questions asked

**Q1:** What decision should the board make with this dashboard? For example: set next year's budget, decide which product categories to invest in, or decide which marketing channels to fund?
*Why:* The decision the dashboard supports is unknown. It drives the KPIs, breakdowns and comparison.
**A:** The board needs to judge whether Men's and Women's revenue and gross margin are improving year over year, so they can decide where to focus next quarter. It's a quarterly performance check, not a basis for setting next year's budget or choosing marketing channels.

**Q2:** Which orders should count toward revenue? Options: (a) all orders placed, (b) exclude cancelled orders, or (c) exclude cancelled and returned orders, so only sales that were kept.
*Why:* Revenue definition. Cancelled and returned items change both revenue and gross margin.
**A:** (c) Exclude both cancelled and returned orders, so only sales the customer kept count toward revenue.

**Q3:** For gross margin, I suggest this: (revenue minus the product cost of the items sold) divided by revenue. Revenue uses the actual sale price, and cost comes from the product cost. Is that right? Also, should the board see the latest quarter, which is partial (July to September 2026), or only completed quarters?
*Why:* Confirms the gross margin definition and settles how to treat the partial current quarter. Both affect the time range and the year-over-year comparison.
**A:** Yes, that formula matches what I need, as long as the cost and revenue both exclude cancelled and returned items. Show the partial quarter, but label it clearly as quarter-to-date so the board doesn't compare it directly with full quarters.

---

# Requirements Brief

**Business question:** Are Men's and Women's revenue and gross margin improving year over year, quarter by quarter?

**Audience:** The board of directors (non-technical). Quarterly performance check.

**Decision it supports:** Decide where to focus effort next quarter: Men's or Women's. It is not for setting next year's budget or choosing marketing channels.

## KPIs

| KPI | Definition |
|---|---|
| Revenue | Sum of the actual sale price of order items the customer kept. Cancelled and returned items are excluded. Counted by the order date, per quarter. |
| Gross margin (%) | (Revenue minus product cost of the items sold) divided by revenue. Cancelled and returned items are excluded from both revenue and cost. Counted per quarter. |
| Gross margin ($) | Revenue minus product cost of the kept items sold, per quarter. Shown beside the percentage so the board sees both size and rate. |
| Year-over-year change | For revenue and gross margin: this quarter's value versus the same quarter one year earlier. Revenue change is shown in %. Gross margin % change is shown in percentage points. |

## Scope

- **Breakdowns:** Quarter, Department: Men's vs. Women's
- **Filters:** Department (Men's, Women's, or both), Year or quarter range
- **Time range:** Quarterly, from 2019 through the current quarter (Q3 2026, July to September). Q3 2026 is shown as quarter-to-date and clearly labeled.
- **Comparison:** Year over year: each quarter versus the same quarter of the prior year. The quarter-to-date is compared with the same part of the quarter a year earlier, not the full prior quarter.

## Assumptions to approve

- Product department field defines Men's and Women's. Any other departments in the data are left out of the dashboard.
- Quarters are calendar quarters (Q1 = Jan to Mar). Please confirm if the fiscal year differs.
- Revenue is dated by order date, not by the date of shipment or delivery.
- Revenue is before tax and shipping, and uses the actual sale price rather than the list retail price. Please confirm.
- The quarter-to-date comparison uses the same date span in the prior year. I assumed this because it is the only fair comparison.
- Orders that were returned count as excluded in the quarter they were originally placed. Revenue for past quarters can therefore change slightly as late returns come in.
- Includes data from 2019 on so the board sees the long-term trend. The last four to eight quarters can be the default view if this is too busy.

## Out of scope

- Budget planning for next year: not the purpose of this dashboard, so no forecasts or targets are included.
- Marketing channel performance: the board said it is not needed for this decision.
- True profit (net of shipping, marketing, overhead, or returns handling): the data has only product cost and retail price, so only gross margin on product cost can be shown.
