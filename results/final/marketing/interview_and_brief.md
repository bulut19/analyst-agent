**Q1:** What decision will this dashboard help you make? For example: (a) where to spend more or less marketing budget, (b) which channels bring the best customers, or (c) just a regular check on how each channel is doing?

**A:** It's (b) mostly, with a bit of (a): I want to see which channels bring customers who come back and buy again within 12 months, so I can shift budget toward them next quarter. A regular check alone wouldn't help me.

**Q2:** Let's pin down "come back and buy again". Which do you mean? (a) the share of customers who place a second order within 12 months of their first order, (b) the average number of orders per customer in their first 12 months, or (c) both. And should cancelled or returned orders count as purchases?

**A:** I mean (a): the share of each channel's customers who place a second order within 12 months of their first. Cancelled or returned orders shouldn't count, since a refund isn't a real repeat purchase.

**Q3:** Which customers should be included, and over what period? For example: (a) customers whose first order was in the last 3 full years that have had 12 months to come back, (b) all customers since 2019, or (c) something else? Note that customers who first bought in the last 12 months have not had the full 12 months yet.

**A:** Customers whose first order was in the last 2 years, so I get a monthly view. Leave out anyone who first bought less than 12 months ago, since they haven't had time to come back yet and would make their channel look worse than it is.

**Q4:** Two quick things. Who will read this dashboard (for example, you alone, the marketing team, or leadership)? And besides channel and month of first order, do you want to split the results by anything else, such as customer gender, age group, country, or first-purchase product category?

**A:** Mainly me, and I'll share the channel results with my CMO. No other splits needed; channel and first-order month are enough.

**Q5:** Data runs to September 2026. "Last 2 years" with the 12-month rule would leave only first orders from October 2024 to September 2025 (12 monthly groups). Is that fine, or do you want a full 24 months of first orders (October 2023 to September 2025), which uses older customers?

**A:** Let's use the full 24 months, October 2023 to September 2025. That gives me the two-year monthly view I asked for, and everyone in that window has had their 12 months to come back.

---

# Requirements Brief

**Business question:** Which marketing channels bring customers who place a second order within 12 months of their first order?

**Audience:** The requester (primary), who will share the channel results with the CMO.

**Decision it supports:** Which channels to shift marketing budget toward next quarter, based on which channels bring customers who buy again.

## KPIs

| KPI | Definition |
|---|---|
| 12-month repeat purchase rate | Of the customers in a channel whose first valid order fell in the chosen month, the share who placed a second valid order within 12 months of their first valid order. Valid orders exclude cancelled and returned orders. Customers with no valid order are excluded. Calculated per channel and per first-order month, plus a total per channel across the full window. |
| New customers (first-time buyers) | Number of customers whose first valid order fell in the month, by channel. Shown as the base for the repeat rate so small channels or months are not over-read. |
| Repeat customers | Number of those new customers who placed a second valid order within 12 months of their first. This is the numerator of the repeat rate. |

## Scope

- **Breakdowns:** Marketing channel the customer came from, Month of first valid order
- **Filters:** Marketing channel, First-order month
- **Time range:** Customers whose first valid order was between October 2023 and September 2025 (24 monthly groups). Each has had at least 12 months of follow-up, using data to September 2026. Later first-time buyers are excluded because they have not had 12 months yet.
- **Comparison:** Channels compared with each other, by month and in total over the 24 months. No comparison to a prior period.

## Assumptions to approve

- 'First order' means the customer's first valid order (not cancelled or returned). A customer whose first order was cancelled or returned is counted from their first valid order instead.
- 'Within 12 months' means the second valid order is dated no later than 12 calendar months after the first valid order date.
- A returned order is excluded entirely, even if only part of it was returned. Please confirm whether partly returned orders should count.
- Each customer has one marketing channel, the one stored on their customer record, which is assumed to be the channel that acquired them.
- Customer counts per channel per month may be small, so the monthly view could be noisy. The total per channel over 24 months is the more reliable comparison.
- The window is based on the date of first order, not the date the customer signed up.

## Out of scope

- Marketing spend, cost per customer and return on budget: the data has no marketing spend or campaign cost, so the dashboard can show which channels bring repeat buyers but not which are the most cost-efficient. The budget decision will need spend figures from elsewhere.
- Repeat behaviour for customers whose first order was after September 2025: they have not had 12 months yet, so they are left out as requested.
