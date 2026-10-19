**Q1:** What decision will this help you make? For example: (a) fix problem products or brands, (b) change a return policy, (c) find which customers or channels send back the most, or (d) something else?

**A:** (a) Fix problem products or brands. I want to see which categories and brands to review with suppliers, so I'm focusing on the ones with enough volume to matter.

**Q2:** How should we measure "returns"? Option 1: share of items sold that were returned (returned items ÷ items sold). Option 2: share of orders with at least one returned item. Option 3: the money value of returned items (at retail price). Which one, or a combination?

**A:** Option 1, returned items divided by items delivered or returned, with cancelled items left out. That's the measure I need for picking which categories and brands to take to suppliers.

**Q3:** You want to focus on categories and brands with enough volume to matter. What cut-off should count as enough? For example: at least 100 items sold in the period, at least 500, or the top 20 by items sold. If unsure, I can propose one.

**A:** I don't have a set number. Something like a few hundred items sold over the 12 months seems like enough to be worth a supplier conversation, so go ahead and propose a cutoff.

**Q4:** What time period and comparison do you want? Options: (a) last 12 months only, (b) last 12 months vs the 12 months before, (c) monthly trend over the last 24 months with a 12-month total. Data runs to September 2026.

**A:** Last 12 months only, October 2025 through September 2026, with a month-by-month trend. I don't need the comparison to the prior year.

**Q5:** Who will read this dashboard? For example: just you, the merchandising/buying team, or senior leadership? And do you want to be able to filter by department (e.g. Men/Women) too?

**A:** Mostly me, and the merchandising team will probably look at it too. I don't need a department filter; category and brand are enough.

---

# Requirements Brief

**Business question:** Which product categories and brands have the highest return rates over the last 12 months (October 2025 to September 2026), among those with enough sales volume to matter, and how has the return rate moved month by month?

**Audience:** The requester (primary) and the merchandising team.

**Decision it supports:** Choose which categories and brands to review with suppliers because of high return rates.

## KPIs

| KPI | Definition |
|---|---|
| Return rate (items) | Returned items divided by items that were delivered or returned. Cancelled items are left out of both the top and the bottom. Items still in process or shipped but not yet delivered are also left out. Calculated over October 2025 to September 2026. |
| Items sold (volume) | Count of items that were delivered or returned (same base as the return rate denominator), over October 2025 to September 2026. Used to apply the volume cut-off. |
| Returned items | Count of items with a return, over October 2025 to September 2026. Shown next to the rate so the size of the problem is clear. |

## Scope

- **Breakdowns:** Product category, Brand, Month (for the trend)
- **Filters:** Category, Brand
- **Time range:** October 2025 through September 2026 (last 12 months), with a month-by-month trend.
- **Comparison:** None. No comparison to the prior year. Overall company return rate shown as a reference line only if approved (see assumptions).

## Assumptions to approve

- Volume cut-off: a category or brand needs at least 300 items delivered or returned across the 12 months to be ranked. Those below are hidden from the ranking (or shown as 'low volume'). Please approve or change the number.
- Items are assigned to a month by the order date, not the return date. Please confirm.
- Items that are still processing or shipped (not yet delivered) are excluded, since their outcome is unknown. This follows from the stated definition.
- Monthly trend is shown for the overall rate and for any selected category or brand. Monthly figures for small brands may be noisy.
- The company-wide return rate is shown as a benchmark so the reader can see whether a category or brand is above or below average. This was not requested and needs approval.
- Return rate is counted in items, not orders or money value, as the stakeholder chose.

## Out of scope

- The reasons for returns (e.g. wrong size, defective) cannot be shown unless the data records them. The data described covers orders, items, products and customers, with no return reason.
- Supplier-level analysis is not possible as a separate view. The data has brand but no supplier field, so brand is used as the proxy.
- Comparison to the prior year was not requested and is not included.
