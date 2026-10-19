**Q1:** What do you mean by "repeat purchase"? For example: (a) a customer who places a second order at any time after their first, (b) a customer who orders again within a set window, like 90 days, or (c) the share of this year's orders that come from returning customers?

**A:** I mean (b), but with a 12-month window: a customer counts as a repeat buyer if they place at least two orders within 12 months of their first order. I'm not interested in (a) or (c).

**Q2:** What decision will this dashboard help you make? For example: (a) where to spend marketing budget, (b) which products or categories to fix or promote, or (c) whether to start a loyalty or win-back program?

**A:** The decision is whether we need a loyalty or win-back program. If repeat buying has fallen, I'll put retention spend there instead of more acquisition.

**Q3:** Data runs to September 2026. A customer needs 12 full months to count as repeat or not. So customers who first ordered after September 2025 can't be judged yet. That means "this year" (2026) can't be measured fully. Which would you prefer? (a) Compare groups of customers by the year of their first order, using only complete groups (2025 vs 2024 and earlier). (b) Same, but by month of first order, up to September 2025, so you see the latest trend. (c) Something else.

**A:** (a). Compare full-year groups, 2025 against 2024 and earlier. A partial 2026 wouldn't be reliable anyway.

**Q4:** Should cancelled or returned orders count as orders? For example: (a) count every order placed, (b) exclude cancelled orders only, or (c) exclude both cancelled and returned orders?

**A:** Exclude cancelled orders, since they were never really purchases. Keep returned orders, since the customer still chose to buy.

---

# Requirements Brief

**Business question:** Did the share of new customers who buy again within 12 months fall for the 2025 first-order group compared with 2024 and earlier groups, and which customer or product groups explain the drop?

**Audience:** Stakeholder who decides retention vs acquisition spend (business leadership / marketing). Assumed non-technical.

**Decision it supports:** Whether to fund a loyalty or win-back program and shift spend from acquisition to retention.

## KPIs

| KPI | Definition |
|---|---|
| 12-month repeat buyer rate | Of customers whose first order was in a given year, the percent who placed at least 2 orders within 12 months of their first order. The first order counts as order 1. Cancelled orders are excluded. Returned orders are included. Only full-year groups with a complete 12-month window are shown (2019 to 2025 first-order years). |
| Repeat buyers (count) | Number of customers in each first-order year group who met the 12-month repeat rule above. |
| New customers (count) | Number of customers whose first non-cancelled order fell in each year. This is the base for the rate. |
| Change in repeat rate vs prior groups | Difference in percentage points between the 2025 group's rate and the 2024 group's rate, and versus the average of earlier groups. |

## Scope

- **Breakdowns:** Marketing channel the customer came from, Product category of the first order, Department of the first order, Brand of the first order, Customer gender, Customer age band, Customer location (country/state), Time between first and second order (distribution, in whole days)
- **Filters:** First-order year, Marketing channel, Product category, Department, Gender, Age band, Location
- **Time range:** Customer groups by year of first order, 2019 to 2025. Each customer is followed for 12 months after their first order, so follow-up runs to the end of 2026 for the 2025 group, which is available only up to September 2026 data. See assumptions on this.
- **Comparison:** 2025 first-order group vs 2024 group, and vs earlier groups (2019–2023).

## Assumptions to approve

- Because data ends in September 2026, customers whose first order was after September 2025 have no full 12 months. The 2025 group is only complete for customers whose first order was January to September 2025. Proposal: for 2025, include only first orders from January to September 2025, and compare with the same January–September months in earlier years. Please approve, or tell us to show 2025 as partial.
- 'This year' is read as the 2025 group, the latest complete group, not calendar 2026. 2026 is not shown.
- The 12-month window is 365 days from the date of the first order.
- A customer's first order is their earliest non-cancelled order. If their first order was cancelled, the next non-cancelled order becomes the first.
- The two or more orders must be separate non-cancelled orders. Several items in one order count as one order.
- Whole days are used for the time-between-orders view, not hours.
- Breakdowns by category, department and brand use the first order's items. If a first order has several categories, the customer is counted in each. Totals across categories may therefore exceed the total customers.
- Customer attributes (channel, age, gender, location) are taken as currently recorded, not as at the first order date.

## Out of scope

- Repeat buying in 2026: customers acquired in 2026, or after September 2025, have not had 12 months, so a fair rate cannot be calculated yet.
- The real reasons customers did not return (price, service, delivery, satisfaction, competitors): the data holds orders, products and customer attributes, but no survey, review, or reason data. The dashboard can show where the drop is concentrated, but it cannot prove why.
- Impact of pricing, promotions or discounts on repeat buying, unless discount data is present in order items. Only retail price and cost are known, so this is not assumed.
