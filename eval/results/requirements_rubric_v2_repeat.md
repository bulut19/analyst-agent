# Requirements rubric (v2_repeat)

| Persona | Questions | found_real_need | kpis_unambiguous | useful_questions | flagged_data_limits | approvable_as_written | Avg |
|---|---|---|---|---|---|---|---|
| marketing | 4 | 5 | 4 | 5 | 5 | 4 | 4.6 |
| returns | 4 | 5 | 4 | 5 | 5 | 4 | 4.6 |
| finance | 3 | 3 | 4 | 4 | 4 | 3 | 3.6 |
| merchandising | 4 | 4 | 4 | 4 | 5 | 3 | 4.0 |
| repeat_customers | 4 | 4 | 4 | 5 | 4 | 3 | 4.0 |

**Average: 4.2/5** (judge: claude-opus-5-5)

## Judge comments

- **marketing:** The brief captures the real need: the budget move next quarter, the 12-month repeat rate grouped by first-order month and channel, the monthly view over two years, and the CMO as audience. It also flags the incomplete recent months, the missing spend data and small sample sizes. Gaps: it never lists the five channels, it doesn't say whether the 12-month boundary is inclusive, and several 'please confirm' items mean it needs one more round of approval before sign-off.
- **returns:** Strength: the brief covers everything the stakeholder needed. It names the supplier-review decision, uses their exact return-rate definition with cancelled items excluded, and covers the 12-month window, the monthly trend, the category and brand breakdowns, and the 500-item volume minimum. It also openly flags the return-lag effect and the possibly incomplete latest month. Gap: a few points are still open and need sign-off. The trend month (order date or return date) and the exact 12-month window are left for the requester to confirm. The overall reference line was never requested, and the out-of-scope list is empty. So it needs a short confirmation round before it can be fully approved.
- **finance:** The brief defines revenue and gross margin % precisely, including exclusions, order-date attribution, ratio of totals and pp change, and it lists the assumptions about timing, status and partial periods clearly. It misses the main grain the stakeholder needs: monthly figures across 2025 and 2026, with quarters as an extra. Because no question asked about time granularity, the dashboard is built only on quarters and YTD, and the brief needs revising before sign-off.
- **merchandising:** Main strength: the brief gets the decision, period, category grouping and both flag conditions right, and it defines units sold, actual-price margin, ties and edge cases (zero sales, new launches) carefully and honestly. Main gap: revenue is never listed as a KPI to show for each product, even though the stakeholder needs units, revenue and margin. Q3 also bundles audience, cancellations and returns into one question, and the brief leaves several 'please confirm' items open, so a manager would likely ask for changes before signing off.
- **repeat_customers:** Strength: four well-chosen questions led to a clear 12-month repeat purchase rate grouped by first-order year, with an exact cancelled/returned rule and the cohort size and numerator shown, and the brief honestly says that a full 12-month comparison of 2026 is impossible and that cause is out of scope. Gap: the stakeholder asked for the rate by country with the US separated, but the brief folds every non-US country into one "international" group, and it leaves fuzzy points a manager would send back: an unexplained 2019 start, and "about September" instead of an exact data end date and incomplete-cohort cutoff.
