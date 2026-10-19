Automated data quality checks have run on the tables behind this dashboard. Each finding below lists
the rule that failed, how many rows broke it, and a few sample rows.

The checks are deliberately strict, so some findings are not real problems. Judge each one:
- real_issue: the data is wrong or unreliable in a way that would distort numbers.
- expected: the rule fired, but the data is correct for this business (explain why).
- false_alarm: the check misread valid data (for example, two genuinely different names that look alike).

For each finding, give:
1. verdict and severity. Severity reflects how much it would distort the KPIs in this brief, not the
   row count. A few rows can be high severity if they inflate a total (for example, a 999-item order);
   thousands of rows can be low if no KPI uses that column. Use "none" for expected and false alarms.
2. the KPIs it affects (by name, from the brief), or an empty list.
3. a plain-language explanation a manager would understand.
4. a proposed cleaning rule, stated precisely enough to implement (for example: "exclude order items
   with sale_price <= 0"), or "none".
5. whether it needs a business decision, and if so, the question to ask the stakeholder.

Rank real issues first, by severity. Call submit_audit once.
