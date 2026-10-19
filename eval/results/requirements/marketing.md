# Interview: marketing

**Request:** Can you build me a dashboard on how our marketing channels are doing?

**Hidden need (what the simulator knew):** You want to know which traffic sources (Search, Email, Facebook, Display, Organic) bring customers who buy again, not just once. You care about the share of each channel's customers who place a second order within 12 months. Monthly view over the last 2 years. You will use it to move budget between channels next quarter. You report to the CMO.

## Questions asked

**Q1:** What decision will this dashboard help you make? For example: (a) where to spend more or less marketing budget, (b) which channels bring the best long-term customers, or (c) a regular performance report for leadership?
*Why:* Decision supported is the top priority and is entirely open. It shapes KPIs, comparison and audience.
**A:** It's for deciding where to spend more or less marketing budget next quarter, specifically based on which channels bring customers who come back. The answer is (a), informed by (b). I'd want to see repeat purchase rate within 12 months by channel, monthly, for the last two years.

**Q2:** Let me confirm how to count "repeat purchase rate within 12 months". I propose this: take customers whose first order was in a given month. Count the share who placed a second order within 12 months of their first order. Cancelled and returned orders would not count. Is that right? If not, what should change?
*Why:* Defines the core KPI: cohort basis (first order month), repeat definition, exclusions of cancelled/returned orders. Also sets up the immaturity issue for recent cohorts.
**A:** Mostly yes, with two changes. Only count a cohort once its full 12 months have passed, so recent months don't look artificially low. And make sure each customer is tagged with the traffic source of their first order, so I can see the rate by channel.

---

# Requirements Brief

**Business question:** Which marketing channels bring customers who place a second order within 12 months of their first?

**Audience:** Marketing decision-maker(s) who set next quarter's channel budget. Exact readers not confirmed.

**Decision it supports:** Where to spend more or less marketing budget next quarter, based on which channels bring customers who come back.

## KPIs

| KPI | Definition |
|---|---|
| 12-month repeat purchase rate | Of customers whose first order was in a given month, the share who placed a second order within 12 months of their first order date. Cancelled and returned orders do not count as orders, for either the first or the second order. A month is shown only once all 12 months have passed for that cohort. Shown by channel. |
| New customers (cohort size) | Number of customers whose first valid (not cancelled, not returned) order fell in the month, by channel. Shown next to the rate so small groups are not over-read. |
| Repeat customers | Number of customers in the cohort who placed a second valid order within 12 months of their first. This is the top half of the rate. |

## Scope

- **Breakdowns:** Marketing channel (the channel the customer came from), Month of first order (cohort month)
- **Filters:** Marketing channel, Cohort month range, Possibly customer gender, age band and location, if wanted
- **Time range:** Monthly cohorts by first-order month, covering the last two years of cohorts that have a full 12 months of follow-up. With data to September 2026, that is first orders from about October 2023 to September 2025. Cohorts after September 2025 are left out until they mature.
- **Comparison:** Channel against channel, and each channel's trend month by month. Optionally each channel against the all-channel average. No year-over-year comparison was requested.

## Assumptions to approve

- 'Last two years' means the last 24 matured cohort months (about Oct 2023 – Sep 2025), not the last 24 calendar months to today. Please confirm.
- Returned and cancelled orders are excluded. We assumed this because the stakeholder agreed to the proposal. Please confirm that a returned first order means the customer is not counted as a new customer in that month.
- The data holds one marketing channel per customer, not one per order. We treat it as the channel that brought the customer in, which should match the channel of their first order. Please confirm this is acceptable.
- 12 months means 12 calendar months from the first order date.
- Channels with very few new customers in a month may show noisy rates. We suggest also showing a 3-month or quarterly rolling view.
- Orders in the same basket or placed on the same day as the first order are treated as one order, not a repeat. Please confirm.
- Reader list and any extra filters (age, gender, location) are not confirmed.

## Out of scope

- Return on marketing spend, cost per new customer and any budget-vs-result view: the data has no marketing spend by channel. Only product cost and retail price are held.
- Channel of each individual order: only one channel per customer is held, so we cannot see which channel drove repeat orders.
- Repeat rate for customers acquired after about September 2025: they do not yet have a full 12 months of history, so they are excluded by design.
- Forecasting how much budget each channel should get: the dashboard shows past repeat behaviour only.
