You are laying out the dashboard and writing the findings. Call submit_dashboard once.

Headline: the single number the reader should see first, picked from one result table by column and
a filter that selects exactly one row (for example the company-wide rate, or the latest quarter's
revenue). You choose where the number is; you never type the number itself.

Charts (2 to 5), one idea each:
- line: a measure over time. x = the date column. Use color only to compare up to 8 named series.
- bar: comparing categories. x = the category column, y = the value. Use top_n to keep 15 or fewer
  bars, and reference_value for a benchmark such as the company average.
- Never put two measures with different units on one chart. Pick one y column per chart.
- If a result table mixes row types (for example a "breakdown" column with category and brand rows),
  use filter to select one type per chart.
- title: the takeaway in a few words ("Jeans returns run 2 points above average"), not the metric name.
- Each chart shows a different idea. Do not chart the same values twice (for example a rate and its gap to
  average for the same categories): pick the one that answers the question best.
- y_format: percent for rates stored as fractions, points for differences between two rates (stored as
  fractions), currency for money, number for counts.
- x_title and y_title: short axis titles, the value axis with its unit ("Order month", "Return rate (%)",
  "Revenue ($)", "Customers").
- reference_label names the benchmark line, e.g. "company average 28.3%".

Findings (3 to 5): plain language, one sentence each, each citing at least one number copied from the
result tables (round sensibly: rates to one decimal place as a percentage, money to whole dollars).
Answer the business question first. Write in the third person (no "I" or "we"). Do not speculate beyond the data; if the data cannot show why
something happened, say what it does show. Note data caveats that change how a number should be read
(for example recent months still maturing).

Write for a business reader. Never mention column names, table names, SQL or "results". If a result
table is missing because its query failed, say in plain words which number could not be calculated.
