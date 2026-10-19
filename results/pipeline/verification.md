# Spot checks: agent numbers vs. independent SQL

Hand-written queries on the clean copy, compared with the agent's results on the dirty copy after cleaning.

| Brief | Number checked | Agent result | Independent query | Match |
|---|---|---|---|---|
| Returns | Jeans return rate, Oct 2025 to Sep 2026 | 30.29% (477 of 1,575) | 30.29% (1,575 items) | Exact |
| Returns | Swim return rate, same window | 27.07% (386 of 1,426) | 27.07% (1,426 items) | Exact |
| Returns | Company-wide return rate | 28.251% | 28.247% | Difference = planted bad rows the agent excluded |
| Finance | Q1 2026 revenue, Women | $298,782.23 | $298,782.23 | Exact |
| Finance | Q1 2026 revenue, Men | $324,278.26 | $324,428.26 | $150.00 gap = planted order item 125777 (sale price set to an invalid value), correctly excluded |

The two "Jeans" spellings planted in the dirty copy were mapped back by the cleaning rule, which is why the
Jeans count matches the clean copy exactly.
