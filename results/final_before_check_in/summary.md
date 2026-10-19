# Final evaluation: 5 stakeholder personas, end to end

| Persona | Questions | Rubric (1-5) | Metrics OK | SQL retries | Findings grounded | Minutes | Agent cost |
|---|---|---|---|---|---|---|---|
| finance | 4 | 3.8 | 4/4 | 0 | yes | 3.6 | $0.33 |
| marketing | 3 | 4.2 | 3/3 | 0 | yes | 4.1 | $0.38 |
| merchandising | 3 | 4.6 | 4/4 | 1 | yes | 4.1 | $0.39 |
| repeat_customers | 4 | 3.2 | 4/4 | 0 | yes | 6.1 | $0.49 |
| returns | 3 | 4.6 | 3/3 | 0 | yes | 3.7 | $0.32 |

**Averages:** rubric 4.1/5, 18/18 metrics OK, 4.3 minutes and $0.38 per run.

## Rubric detail (judge model: claude-opus-5-5)

| Persona | found_real_need | kpis_unambiguous | useful_questions | flagged_data_limits | approvable_as_written | Comment |
|---|---|---|---|---|---|---|
| finance | 3 | 4 | 4 | 5 | 3 | The brief gets the revenue and gross margin definitions right (cancelled and returned items excluded, margin on the same base, revenue counted by order quarter). It also handles the department split, the partial Q3 2026 and the missing targets well. Its biggest gap is the time detail: the stakeholder mainly wanted monthly figures with quarterly totals as a bonus, but the brief only shows quarters. That happened because Q3 offered only quarterly choices. It also drops Q4 2025 from the 2025 data, which needs fixing before sign-off. |
| marketing | 4 | 4 | 4 | 5 | 4 | Strength: the brief covers the core need. It names the decision (moving budget next quarter) and defines a clear 12-month repeat purchase rate on completed orders only, with monthly cohorts across the last 2 years. It is also honest about limits, flagging that there is no spend data, that monthly cohorts may be small, and that each customer has a single channel on their record. Gap: the audience was guessed as the marketing lead instead of being asked, and the stakeholder actually reports to the CMO. The 12-month window (365 days or 12 calendar months) and how to treat a second order on the same day are also left open, so two analysts could still get slightly different numbers. |
| merchandising | 5 | 4 | 5 | 5 | 4 | The brief captures the full hidden need in three well-chosen questions: the bottom-10%-by-units AND margin-below-20% rule, the last 12 months, grouping by category, the units/revenue/margin columns, and the buying-plan decision. It also states its assumptions clearly (cancellations, ranking across all products rather than within each category, ties, new launches). Small gaps keep it from full marks: the time range says roughly Oct 2025–Sep 2026 and also says to fall back to the prior 12 full months if September is incomplete. The per-unit cost basis (current vs. historical cost) is not pinned down, and the new-launch treatment is left for the stakeholder to approve. |
| repeat_customers | 3 | 4 | 3 | 4 | 2 | Strength: the brief gets the KPI exactly right (2 or more non-cancelled orders within 12 months of the first order, grouped by first-order year). It also sees that 2026 cannot be measured and is honest about what the data cannot explain. Gap: the analyst never asked about breakdowns, so the US vs international split by country is missing and is replaced by a long list of unrequested dimensions. The business question also assumes there was a drop, when the stakeholder wants to hear if there wasn't one. And the brief contradicts itself on whether the 2025 group is complete: Q3 and the KPI text say it is, while the assumptions propose limiting it to Jan–Sep first orders. |
| returns | 5 | 4 | 5 | 5 | 4 | Main strength: the brief covers the whole hidden need. It names the supplier-review decision, the return rate by category and brand, the 12 months with a monthly trend, the stakeholder's exact definition with cancelled items left out, and a 500-item volume cut-off. It also honestly flags the order-date vs return-date choice, possible partial months and the missing return-reason data. Main gap: there are small inconsistencies and unrequested additions. The time range is called '12 complete months (Oct 2025–Sep 2026)' but September may be partial, the base is labelled 'items sold' when it means delivered or returned items, and a Department filter and company-wide benchmark were added without being asked for. |

Minutes include the simulated interview. Agent cost excludes the judge model.
