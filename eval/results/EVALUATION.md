# Evaluation results

| Test | Setup | Result | Target |
|---|---|---|---|
| Data quality audit: recall | 40 planted errors, 8 types, answer key | **40/40 (100%)** caught by the right check | 90%+ |
| Data quality audit: precision | New flagged rows vs. clean copy | **40/40 (100%)** were planted errors | 80%+ |
| Data quality audit: false alarms | Same checks on the clean copy | **0** high-severity; 2 look-alike names (Kagawa/Kanagawa, Austria/Australia) correctly dismissed by the LLM | ~0 |
| SQL accuracy | 25 golden questions (8 easy, 9 medium, 8 hard), answers verified by hand | **25/25 (100%)** | 80%+ |
| Requirements quality | 5 simulated stakeholders with hidden needs, scored 1-5 on 5 criteria by a separate judge model | **4.2/5** (v2 prompt, 2 runs: 4.3 and 4.2); v1 prompt scored 3.9 | 4+ |
| End to end | 5 full runs, request to dashboard | **4.8 min** and **$0.46** per run on average; **19/19** metrics computed; all findings grounded in the data | < 5 min, < $0.50 |
| Check-in before building | Questions the agent asks after drafting the metrics, answered by the simulated stakeholder | **7** questions across 4 of 5 runs (none for the finance request, which was already specific); all 7 changed which rows appear or the headline; the stakeholder overruled the agent's default on **2 of 7** | Material questions only, at most 2 per run |

Details: [audit](audit/summary.md) · [SQL accuracy](sql_accuracy.md) · [end-to-end runs](final/summary.md) ·
[rubric v2](requirements_rubric_v2.md) · [rubric v2 repeat](requirements_rubric_v2_repeat.md) ·
[number spot checks](pipeline/verification.md)

## What the evaluation changed

- **Interview prompt v1 → v2 (3.9 → 4.2).** The judge's comments showed the agent skipped questions about
  breakdowns and audience, offered only "quarterly" when the stakeholder wanted "monthly with quarterly totals",
  took "Why did repeat purchases drop?" as fact, and sometimes contradicted itself inside the brief. Four
  prompt rules fixed these.
- **Golden question M9.** The test, not the agent, was wrong (whole hours vs exact time). The fix also
  added a rule: the interview now confirms units and precision for time-based KPIs.
- **Empty results.** A "which products should we stop selling?" request had a true answer of zero products
  (no product in this data has a margin under 20%). The SQL check treated "no rows" as an error; it now asks
  for a query that reports 0.

- **Ratios with nothing to divide by.** A per-product margin failed for products with zero sales: margin was
  blank, and the sanity check rejected blank columns three times. Two fixes: the metric plan must now state
  what happens when a ratio has nothing to divide by (and list it for the stakeholder to approve), and a
  column may be blank only if the agent gives the business reason. Rerun: all metrics computed.

- **Asking instead of assuming.** The interview happens before the agent has seen the data, so issues like
  "unsold products have no margin" only surface later, in the metric plan. The agent used to pick a default
  and list it under "Decisions assumed". Now, after drafting the metrics, it asks the stakeholder about at
  most 2 decisions that change which rows appear or the headline, with a recommended option, and revises the
  plan before writing any SQL. Minor choices are still listed as assumed. In the rerun, 2 of 7 answers
  overruled the agent's default (for example, the repeat-purchase stakeholder asked for a 6-month same-time
  comparison so recent groups are not unfairly low), and the merchandising dashboard now reports unsold
  products as their own "No sales" group. Cost: about 0.5 minutes and $0.08 more per run.

- **Rounding twice.** A screenshot review caught the returns headline at 28.2% while the findings said 28.3%.
  The model had been shown rates rounded to 4 decimals (0.2825) and rounded again. It now sees 6 decimals, and
  the grounding check only accepts a percentage that rounds correctly from the data. The 5 final dashboards
  were rebuilt from the same SQL results; all findings grounded.

## Known limitations

- 5 personas and 25 questions are small samples, and LLM outputs vary run to run (rubric 4.3 vs 4.2 on the same prompt).
- The golden questions spell out their definitions, so they test translating a clear question into SQL;
  handling vague requests is what the interview rubric measures.
- The grounding check confirms each number exists in the results, not that it describes the right thing (a
  number can match a different row). In 1 of 5 runs (merchandising), two metrics disagreed on how many products
  were flagged; the dashboard pointed this out in its findings instead of hiding it.
- The check-in questions were reviewed by hand, not scored by the judge.
- The rubric is scored by an LLM judge (a different, larger model than the agent), not by people.
- The audit catches the 8 error types it was designed for; error types outside those were not tested.
