You are mapping an approved requirements brief to the data. Call submit_mapping once.

For every KPI, dimension, filter and the time range in the brief:
- List the exact table.column names needed, using only names from the schema below.
- Explain in one or two sentences how the columns produce the item (which status values count,
  which date column defines the period, which table is the grain).
- Name the join path between tables.

Then check the brief against the data honestly:
- gaps: anything in the brief the data cannot support, or can only approximate. Give the reason and,
  where possible, the closest available substitute. Do not invent columns to fill a gap.
- data_notes: facts about the data that affect the numbers (for example, a column that is recorded per
  customer rather than per order, a date range limit, or status values that need a decision).

Prefer order_items as the grain for revenue, cost, margin and returns, because status and price are recorded per item.

# Schema
{schema}
