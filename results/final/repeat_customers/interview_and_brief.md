**Q1:** What decision will this help you make? For example: change a marketing campaign, adjust a loyalty offer, or report to leadership.

**A:** We're deciding whether our retention efforts are working, and if repeat purchases have fallen, where to focus fixes. That will shape how we adjust our loyalty offers and what we report to the leadership team.

**Q2:** How should we measure "repeat purchases"? Options: (a) the share of customers who placed a 2nd order within 90 days of their first; (b) the share of this year's buyers who had also bought before; (c) the number of orders from returning customers. Or tell me your own.

**A:** None of those quite fits. Use the share of customers who placed a second order within 12 months of their first order, grouped by the year of their first order.

**Q3:** To find where to focus fixes, how should we split the repeat rate? Options: by the marketing channel customers came from, by product category of the first order, by customer age or gender, or by location. Pick any, or say "all".

**A:** Split it by location: the US on its own, then international by country.

**Q4:** Who will read this dashboard: the leadership team, the loyalty/marketing team, or both?

**A:** Mainly the leadership team, since it's going into what we report to them. The loyalty and marketing team may look at it too, but leadership is the primary audience.

**Q5:** Customers who first ordered in the last 12 months haven't had a full year to reorder yet. So 2026 can't be fully measured, and 2025 is only partly measurable. How should we handle it? Options: (a) show only customers with a full 12 months of history, so the latest complete group is first orders through September 2025; (b) also show 2025 and 2026 with a "not yet complete" label; (c) both, with the incomplete years shown separately.

**A:** I'd go with (c). I need to see 2026 to answer whether repeat purchases dropped, but leadership shouldn't read partial numbers as final, so keep the incomplete years visibly separate and labeled.

---

# Requirements Brief

**Business question:** How has the 12-month repeat purchase rate changed across customer groups by year of first order (2019 to 2026), and in which locations (US vs. each international country) is any change concentrated?

**Audience:** Leadership team (primary). The loyalty and marketing team may also use it.

**Decision it supports:** Whether retention efforts are working and, if the repeat rate has fallen, which locations to focus fixes on. This will shape loyalty offer changes and what is reported to leadership.

## KPIs

| KPI | Definition |
|---|---|
| 12-month repeat rate | Of the customers whose first order was in a given year, the share who placed a second order within 12 months of their first order date. Customers are grouped by the year of their first order. A second order is a separate, later order by the same customer. Customers with only one order count in the base but not as repeaters. |
| First-time customers (group size) | Number of customers whose first order was in the given year. Shown so readers can see how big each group is. This is the base for the repeat rate. |
| Repeat customers | Number of those first-time customers who placed a second order within 12 months of their first order. This is the top of the repeat rate. |

## Scope

- **Breakdowns:** Year of first order (customer group), Location: United States as one group, then international customers by country
- **Filters:** Year of first order, Location (US / country)
- **Time range:** Customers by year of first order, from 2019 to September 2026 (the latest data). Complete groups (a full 12 months of history after first order) are shown in the main view. Incomplete groups are shown in a separate section, clearly labeled "not yet complete: not final".
- **Comparison:** Year over year: each first-order year compared with earlier years. 2026 is compared with prior years, with a clear label that it is partial.

## Assumptions to approve

- 'Within 12 months' means the second order date is no more than 12 calendar months after the first order date.
- Cancelled orders are not counted as orders (neither as first nor second order). Returned orders still count. Please confirm or change.
- The first order is the customer's earliest order in the data. Customers who ordered before 2019 are not visible, so any who did would be wrongly treated as new in 2019.
- Complete groups are customers whose first order was at least 12 months before the last date in the data (first orders up to September 2025). Because of this cut-off, 2025 is split: January to September 2025 is complete and October to December 2025 is incomplete. I assume the incomplete part of 2025 and all of 2026 go in the separate labeled section. Please confirm.
- For incomplete groups, the rate uses only the time observed so far, so it will look lower than a full 12-month rate. It should not be read as a like-for-like drop. Please confirm this treatment, or ask for a same-elapsed-time comparison against earlier years.
- Location is the customer's location on file (country, with the US shown on its own). It may not be where they lived at the time of the first order. Customers with a missing location go into an 'Unknown' group.
- 'This year' means 2026, based on data through September 2026.

## Out of scope

- Explaining why repeat purchases changed. The data shows when and where the rate moved, not the cause. Any cause would be a hypothesis to test.
- Judging whether loyalty offers or retention programs worked. The data has no record of loyalty offers, campaigns sent, or who received them. The dashboard can only show whether the repeat rate moved.
- Final 2026 repeat rate. Most 2026 first-time customers have not had 12 months yet, so 2026 can only be shown as partial.
