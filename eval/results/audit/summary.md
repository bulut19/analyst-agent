# Audit Evaluation

| Metric | Result | Target |
|---|---|---|
| Recall: planted errors caught by the right check | 40/40 (100%) | 90%+ |
| Precision: new flagged rows that are planted errors | 40/40 (100%) | 80%+ |
| Findings containing planted errors that the LLM called real issues | 9/9 | all |
| Clean copy: findings | 6 | |
| Clean copy: high-severity real issues (should be genuine pre-existing problems) | 0 | review |

## Recall by error type

| Error type | Caught |
|---|---|
| duplicate_order | 5/5 |
| missing_user_id | 5/5 |
| delivered_before_created | 5/5 |
| outlier_quantity | 5/5 |
| future_order_date | 5/5 |
| invalid_price | 5/5 |
| orphan_product | 5/5 |
| inconsistent_category | 5/5 |

## Every planted error

| ID | Type | Row | Flagged by |
|---|---|---|---|
| E01 | duplicate_order | order_id=89217 | duplicate_key |
| E02 | duplicate_order | order_id=15510 | duplicate_key |
| E03 | duplicate_order | order_id=3480 | duplicate_key |
| E04 | duplicate_order | order_id=103490 | duplicate_key |
| E05 | duplicate_order | order_id=38360 | duplicate_key |
| E06 | missing_user_id | order_id=34162 | missing_required |
| E07 | missing_user_id | order_id=31153 | missing_required |
| E08 | missing_user_id | order_id=19425 | missing_required |
| E09 | missing_user_id | order_id=102784 | missing_required |
| E10 | missing_user_id | order_id=14292 | missing_required |
| E11 | delivered_before_created | order_id=94880 | date_order |
| E12 | delivered_before_created | order_id=103779 | date_order |
| E13 | delivered_before_created | order_id=124891 | date_order |
| E14 | delivered_before_created | order_id=76570 | date_order |
| E15 | delivered_before_created | order_id=11949 | date_order |
| E16 | outlier_quantity | order_id=82411 | outlier |
| E17 | outlier_quantity | order_id=58888 | outlier |
| E18 | outlier_quantity | order_id=4437 | outlier |
| E19 | outlier_quantity | order_id=4158 | outlier |
| E20 | outlier_quantity | order_id=13087 | outlier |
| E21 | future_order_date | order_id=38138 | future_date |
| E22 | future_order_date | order_id=40765 | future_date |
| E23 | future_order_date | order_id=88137 | future_date |
| E24 | future_order_date | order_id=104803 | future_date |
| E25 | future_order_date | order_id=4591 | future_date |
| E26 | invalid_price | id=157238 | non_positive |
| E27 | invalid_price | id=55882 | non_positive |
| E28 | invalid_price | id=182130 | non_positive |
| E29 | invalid_price | id=152910 | non_positive |
| E30 | invalid_price | id=117591 | non_positive |
| E31 | orphan_product | id=61895 | orphan_key |
| E32 | orphan_product | id=125777 | orphan_key |
| E33 | orphan_product | id=165171 | orphan_key |
| E34 | orphan_product | id=78204 | orphan_key |
| E35 | orphan_product | id=1780 | orphan_key |
| E36 | inconsistent_category | id=21208 | inconsistent_spelling |
| E37 | inconsistent_category | id=21305 | inconsistent_spelling |
| E38 | inconsistent_category | id=1111 | inconsistent_spelling |
| E39 | inconsistent_category | id=28991 | inconsistent_spelling |
| E40 | inconsistent_category | id=16071 | inconsistent_spelling |

## Clean copy findings and the LLM's verdicts

| Check | Table.column | Rows | Verdict | Severity |
|---|---|---|---|---|
| duplicate_value | users.email | 25,534 | real_issue | medium |
| date_order | order_items.created_at, shipped_at | 33,766 | real_issue | medium |
| date_order | order_items.created_at, delivered_at | 5,761 | real_issue | medium |
| date_order | order_items.created_at, returned_at | 637 | real_issue | medium |
| inconsistent_spelling | users.state | 5 | false_alarm | none |
| inconsistent_spelling | users.country | 2 | false_alarm | none |

*Cost of the two LLM reviews: 2 calls, 9,318 in / 4,129 out tokens, $0.060*
