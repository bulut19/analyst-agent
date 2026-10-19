Write one BigQuery Standard SQL query for the metric below. Call submit_sql once.

Rules:
- SELECT only (a WITH clause is fine). No DDL or DML.
- Use only these tables, always written with backticks exactly like this: {tables}
- Use only columns from the schema. Apply every cleaning rule and filter in the definition.
- Use the exact date window given. Use TIMESTAMP comparisons (column >= TIMESTAMP('YYYY-MM-DD')).
- Aggregate to the grain in the definition. Name output columns in snake_case that a reader would
  understand (for example return_rate, items_returned, order_month). Return rates and shares as
  fractions between 0 and 1, not percentages.
- Order time series by date, rankings by the ranking value.
- Ratios (margin, rates, averages) must follow the definition's rule for rows with nothing to divide by;
  use SAFE_DIVIDE so they return blank rather than an error.
- sanity_checks: for each numeric output column, the plausible min and max (for example a rate between
  0 and 1, a count of at least 0). These are checked automatically after the query runs.
  If some blanks are correct (for example unsold products have no margin), say why in blank_allowed_because.

# Schema
{schema}
