**Q1:** What decision should the board make with this dashboard? For example: set next year's budget, decide which product categories to invest in, or check if the company is on track?

**A:** The board should use it to check whether we're on track: how revenue and gross margin compare to last year, quarter by quarter, for Men's and Women's. That's the view I need for the quarterly meeting.

**Q2:** Which orders should count as revenue? Options: (a) all orders placed, (b) exclude cancelled orders, (c) exclude cancelled and returned orders. I suggest (c), which counts only sales the company kept.

**A:** I agree with (c): revenue should be only the sales we kept, so exclude both cancelled and returned orders. Gross margin should be calculated on that same base.

**Q3:** Which quarters should the board see? For example: (a) the last 4 full quarters, each against the same quarter a year earlier, or (b) every quarter since 2019. Note that the data stops in September 2026, so Q3 2026 may be incomplete. Should we show it as a partial quarter or leave it out?

**A:** Show Q1 through Q3 of 2025 and 2026, with each 2026 quarter compared to the same quarter of 2025. I'd include Q3 2026 since the data runs through September, but label it clearly as through September so the board knows it may not be final.

**Q4:** By "Men's and Women's", do you mean the product department (items sold in the Men's or Women's section), or the gender of the customer who bought? I suggest product department.

**A:** Product department, yes. We want to see how the Men's and Women's sections are performing, not who bought the items.

---

# Requirements Brief

**Business question:** How do revenue and gross margin for the Men's and Women's departments in Q1–Q3 2026 compare with the same quarters of 2025?

**Audience:** The board of directors, at the quarterly meeting. Non-technical readers.

**Decision it supports:** Check whether the company is on track compared with last year, by quarter, for the Men's and Women's departments.

## KPIs

| KPI | Definition |
|---|---|
| Revenue | Total sale price of order items that were kept. Cancelled orders and returned items are excluded. Counted by the quarter in which the order was placed. Shown in dollars. |
| Gross margin (dollars) | Revenue minus the product cost of the same kept items. It uses the same base as Revenue: no cancelled or returned items. |
| Gross margin % | Gross margin in dollars divided by Revenue, for the same quarter and department. |
| Year-over-year change | For each 2026 quarter: the change in Revenue, Gross margin (dollars) and Gross margin % versus the same quarter of 2025. Revenue and gross margin dollars are shown as % change. Gross margin % is shown as a difference in percentage points. |

## Scope

- **Breakdowns:** Quarter (Q1, Q2, Q3), Year (2025 vs 2026), Product department (Men's, Women's)
- **Filters:** Product department (Men's / Women's), Quarter
- **Time range:** Q1, Q2 and Q3 of 2025 and 2026. Q3 2026 covers data through September 2026 and is labelled "through September" because it may not be final.
- **Comparison:** Each 2026 quarter against the same quarter of 2025 (year over year).

## Assumptions to approve

- Gross margin is defined as sale price minus product cost, using the product cost on file. Please confirm.
- Quarters are calendar quarters (Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep). Please confirm this matches the company's fiscal year.
- Revenue is assigned to the quarter in which the order was placed, not when it shipped or was returned.
- Returned items are removed from the quarter of the original order. Late returns can lower past quarters slightly, so figures may change over time.
- Revenue excludes shipping, tax and discounts beyond the recorded sale price, because only item sale price is available. Please confirm.
- Only Men's and Women's departments are shown. Any other department is left out.
- The dashboard shows both departments side by side and may also show a combined total. Please say if you want the total.

## Out of scope

- Judging whether the company is 'on track' against a target or budget. The data has no targets or forecasts, so the dashboard can only compare against last year.
- Revenue split by customer gender. You asked for product department, so this is not included.
