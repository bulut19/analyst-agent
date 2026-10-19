**Q1:** What decision will this dashboard help you make? For example: (a) where to move marketing budget, (b) which channels bring the most valuable customers, or (c) tracking channel growth over time?

**A:** It's (a), where to move marketing budget next quarter. I need to see which channels bring customers who come back and buy a second time within 12 months.

**Q2:** Should cancelled or returned orders count as a purchase? For example, if a customer's second order was cancelled, is that still a "second purchase"? Options: (a) only completed orders count, (b) all orders count, or (c) count everything except cancelled.

**A:** Only completed orders should count. A cancelled order isn't a real purchase, so it shouldn't count as a second purchase.

**Q3:** Which customers should we look at? Customers need 12 months of history to be judged fairly. So I suggest only customers whose first completed order was at least 12 months ago (on or before September 2025), grouped by the year they first bought. Is that OK, or do you want a different range?

**A:** The 12-month cutoff works for me, but I need to see the last 2 years by month, not by year. Please group customers by the month of their first completed order so I can compare channels over time.

---

# Requirements Brief

**Business question:** Which marketing channels bring customers who place a second completed order within 12 months of their first?

**Audience:** Marketing lead / budget owner (assumed; not confirmed). Non-technical reader.

**Decision it supports:** Where to move marketing budget next quarter, based on which channels bring customers who come back and buy again.

## KPIs

| KPI | Definition |
|---|---|
| 12-month repeat purchase rate | Of customers whose first completed order was in a given month, the share who placed a second completed order within 12 months after their first completed order date. Only orders with status Completed count. Cancelled and returned orders are excluded, both as first and as second purchases. Shown per channel and per first-order month. |
| New customers (cohort size) | Number of customers whose first completed order fell in a given month, by channel. Shown next to the repeat rate so small groups are easy to spot. |
| Repeat customers | Number of customers in the cohort who placed a second completed order within 12 months of their first. This is the top of the repeat rate. |

## Scope

- **Breakdowns:** Marketing channel the customer came from, Month of first completed order (cohort month)
- **Filters:** Marketing channel, Cohort month range
- **Time range:** Customers whose first completed order was between October 2023 and September 2025 (24 monthly cohorts). Each has a full 12 months to repeat, using data up to September 2026.
- **Comparison:** Channel vs channel, by cohort month, to show trends over the 24 months. Also an overall repeat rate across all channels as a benchmark.

## Assumptions to approve

- 'Last 2 years' means first orders from Oct 2023 to Sep 2025, the latest 24 months with a full 12-month follow-up. Customers who first bought after Sep 2025 are left out because they have not had 12 months yet.
- The 12-month window is counted from the first completed order date, as 365 days (or 12 calendar months). Exact rule to be confirmed.
- A second purchase means a separate completed order on a later date or time than the first. Items in the same order do not count as a second purchase.
- A customer's channel is the single marketing channel stored on their customer record. It is not the channel of each order.
- Monthly cohorts per channel may be small, so we may add a monthly trend with a rolling or quarterly view and show cohort sizes beside the rates.
- Audience is assumed to be the marketing lead or budget owner.

## Out of scope

- Return on marketing spend, cost per customer, and cost per repeat customer: the data has no marketing spend or cost by channel, so the dashboard cannot say which channel is the best value for money. It can only show which channels bring customers who return. Budget moves should also consider spend figures from outside this data.
- Customers who first bought after September 2025: they have not yet had 12 months to repeat, so their 12-month rate is not available.
- Anything about customers who never placed a completed order: they are not part of the cohort.
