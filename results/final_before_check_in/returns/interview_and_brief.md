**Q1:** What decision will this help you make? For example: drop or change certain products or brands, fix a problem with a marketing channel, or change your returns policy?

**A:** We're deciding which product categories and brands to take back to suppliers for a review. So the useful view is return rate by category and brand over the last 12 months, with a monthly trend, leaving out categories that are too small to matter.

**Q2:** How should we measure "return rate"? Options: (a) items returned ÷ items sold, (b) orders with a return ÷ all orders, or (c) money refunded ÷ sales value. For supplier reviews, I suggest (a), because a return is tied to a specific product.

**A:** Option (a) works for us. Returned items divided by items delivered or returned, with cancelled items left out, is the measure we want, since that's how we'll compare brands and categories with suppliers.

**Q3:** What counts as "too small to matter"? For example, leave out any category or brand with fewer than 100, 500, or 1,000 items sold in the 12 months. Which is closest, or do you have another number?

**A:** Let's go with 500 items sold over the 12 months. Anything below that is too small to be worth a supplier conversation.

---

# Requirements Brief

**Business question:** Which product categories and brands have the highest return rates over the last 12 months, and how is the rate changing month by month?

**Audience:** The stakeholder and the people who run supplier conversations (assumed: merchandising or buying team).

**Decision it supports:** Choose which product categories and brands to take back to suppliers for a review.

## KPIs

| KPI | Definition |
|---|---|
| Return rate | Items returned ÷ (items delivered + items returned). Cancelled items are left out of both parts. Each item is counted once. Calculated for the 12-month window, and per month for the trend. |
| Items returned | Number of order items with a return, excluding cancelled items. |
| Items sold (return-rate base) | Number of order items that were delivered or returned. Cancelled items are excluded. This is also the volume used for the 500-item cut-off. |

## Scope

- **Breakdowns:** Product category, Brand, Month (for the trend)
- **Filters:** Product category, Brand, Department (optional, assumed useful)
- **Time range:** Last 12 months of data, as 12 complete months (assumed Oct 2025 to Sep 2026). Monthly trend covers the same 12 months.
- **Comparison:** No comparison requested. Each category and brand is shown against the overall company return rate, and the monthly trend shows change over time.

## Assumptions to approve

- Minimum volume: categories and brands with fewer than 500 items sold (delivered or returned) in the 12 months are left out. Please confirm the cut-off applies separately to categories and to brands, not to brand within category.
- The 12-month window is the latest 12 months in the data. September 2026 may be a partial month. Please confirm whether to use it or end at August 2026.
- Items are assigned to a month by order date, not by return date. Please confirm. The alternative is the return date, which would show when returns happen instead.
- Items still being processed or shipped are excluded, because they are neither delivered nor returned yet.
- The company-wide return rate shown as a benchmark uses the same definition and the same 500-item rule is not applied to it.
- Audience is assumed to be the stakeholder plus the supplier-review team.

## Out of scope

- Reasons for returns (such as size, quality or fit): the data does not hold a return reason, so the dashboard cannot explain why items come back.
- Cost of returns (refund value, shipping, handling): not requested and not defined. Only counts and rates are covered.
