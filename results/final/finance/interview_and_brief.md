**Q1:** What decision should the board make with this dashboard? For example: set next year's budget, decide where to invest in marketing, or check if the business is on track.

**A:** The board should use it to check whether we're on track: how 2026 revenue and gross margin compare with 2025, by quarter, since they meet quarterly.

**Q2:** How should we count revenue? Which orders should be left out? Options: (a) all orders except cancelled ones, (b) all orders except cancelled and returned ones, (c) all orders, whatever their status.

**A:** Option (b). Revenue should be the sale price of items that were neither cancelled nor returned.

**Q3:** Besides the quarterly view, should the board be able to break revenue and margin down by anything? Options: product category, department, marketing channel, or no breakdown (just the totals by quarter).

**A:** Yes, please split it by department, Men and Women. Keep the quarterly view as well.

---

# Requirements Brief

**Business question:** How do revenue and gross margin in 2026 compare with 2025, by quarter, in total and for Men and Women?

**Audience:** The board of directors, who meet quarterly. Readers are non-technical.

**Decision it supports:** Check whether the business is on track in 2026 compared with 2025.

## KPIs

| KPI | Definition |
|---|---|
| Revenue | Sum of the sale price of order items that were neither cancelled nor returned. Items are assigned to the quarter in which the order was placed. Shown in dollars. |
| Gross margin (amount) | Revenue minus the product cost of the same items (neither cancelled nor returned), by quarter. |
| Gross margin % | Gross margin amount divided by revenue, for the same items and quarter. |

## Scope

- **Breakdowns:** Quarter, Department (Men, Women)
- **Filters:** Year (2025, 2026), Department (Men, Women, both)
- **Time range:** Q1 2025 to Q3 2026 (data runs to September 2026). 2026 Q4 is not yet available.
- **Comparison:** Each 2026 quarter against the same quarter of 2025 (year over year), with absolute and % change.

## Assumptions to approve

- Gross margin was not defined by the stakeholder. Assumed: sale price minus product cost, on the same non-cancelled, non-returned items. Please approve.
- Quarters are calendar quarters (Jan–Mar, etc.). Please confirm this matches the company's fiscal year.
- Items are dated by the order creation date, not shipping or delivery date. Please confirm.
- Q3 2026 is assumed to be complete if data runs to the end of September 2026. If September is partial, Q3 will be labelled as partial.
- Revenue is shown before any tax or shipping, as only item sale prices are in the data.
- Only the Men and Women departments exist in the data and are shown. Totals equal Men plus Women.
- Year-to-date 2026 versus the same period of 2025 is shown as a summary, in addition to quarters. This is an addition for approval.

## Out of scope

- Full-year 2026 revenue and margin, and Q4 2026: the data ends in September 2026, so these can't be reported. Any full-year figure would be a forecast, which was not requested.
- Revenue targets or budget comparison: no target or budget data is available, so 'on track' is judged only against 2025.
