"""Draft the golden questions: each has a reference SQL query and the answer it returns on thelook_clean.

Usage (from the project folder):  python -m eval.golden_build
Writes eval/golden_questions.json and eval/golden_questions.md (the review sheet).
Every answer still needs a person to check the reference SQL: set "verified": true once checked.
"""
import json

from google.cloud import bigquery

from agent.config import PROJECT, ROOT

D = f"`{PROJECT}.thelook_clean"
O, I, P, U = f"{D}.orders`", f"{D}.order_items`", f"{D}.products`", f"{D}.users`"
KEPT = "status NOT IN ('Cancelled', 'Returned')"  # item counts as revenue

Q = [
    # ---------------- easy: one table ----------------
    ("E1", "easy", "How many orders were placed in calendar year 2025 (any status)?",
     f"SELECT COUNT(*) AS answer FROM {O} WHERE EXTRACT(YEAR FROM created_at) = 2025"),
    ("E2", "easy", "How many customers signed up through the Facebook traffic source?",
     f"SELECT COUNT(*) AS answer FROM {U} WHERE traffic_source = 'Facebook'"),
    ("E3", "easy", "What share of all orders have the status Cancelled? Give a fraction between 0 and 1.",
     f"SELECT COUNTIF(status = 'Cancelled') / COUNT(*) AS answer FROM {O}"),
    ("E4", "easy", "What is the average age of all customers?",
     f"SELECT AVG(age) AS answer FROM {U}"),
    ("E5", "easy", "How many distinct brands are in the product catalog (ignore missing brands)?",
     f"SELECT COUNT(DISTINCT brand) AS answer FROM {P} WHERE brand IS NOT NULL"),
    ("E6", "easy", "What is the average retail (list) price of products in the Jeans category?",
     f"SELECT AVG(retail_price) AS answer FROM {P} WHERE category = 'Jeans'"),
    ("E7", "easy", "Which country has the most customers? Give the country name.",
     f"SELECT country AS answer FROM {U} GROUP BY country ORDER BY COUNT(*) DESC LIMIT 1"),
    ("E8", "easy", "What is the total sale price of order items with status Complete that were ordered in 2025?",
     f"SELECT SUM(sale_price) AS answer FROM {I} WHERE status = 'Complete' AND EXTRACT(YEAR FROM created_at) = 2025"),
    # ---------------- medium: joins and business rules ----------------
    ("M1", "medium", "What was 2025 revenue from the Women's department? Revenue = sum of order item sale price, "
     "excluding items with status Cancelled or Returned; use the item's order date (order_items.created_at).",
     f"SELECT SUM(i.sale_price) AS answer FROM {I} i JOIN {P} p ON i.product_id = p.id "
     f"WHERE p.department = 'Women' AND i.{KEPT} AND EXTRACT(YEAR FROM i.created_at) = 2025"),
    ("M2", "medium", "Which product category had the highest revenue in 2025? Revenue = sum of item sale price, "
     "excluding Cancelled and Returned items, by item order date. Give the category name.",
     f"SELECT p.category AS answer FROM {I} i JOIN {P} p ON i.product_id = p.id "
     f"WHERE i.{KEPT} AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1 ORDER BY SUM(i.sale_price) DESC LIMIT 1"),
    ("M3", "medium", "What was the average order value in 2025? Order value = sum of sale price of the order's items "
     "that are not Cancelled or Returned; include only orders with at least one such item; use item order dates in 2025.",
     f"SELECT AVG(v) AS answer FROM (SELECT order_id, SUM(sale_price) v FROM {I} "
     f"WHERE {KEPT} AND EXTRACT(YEAR FROM created_at) = 2025 GROUP BY 1)"),
    ("M4", "medium", "What was the item return rate in 2025? Return rate = items with status Returned divided by "
     "items with status Complete or Returned, for items ordered in 2025. Give a fraction.",
     f"SELECT COUNTIF(status = 'Returned') / COUNTIF(status IN ('Complete', 'Returned')) AS answer "
     f"FROM {I} WHERE EXTRACT(YEAR FROM created_at) = 2025"),
    ("M5", "medium", "What was the gross margin percentage in 2025 for items with status Complete? "
     "Gross margin % = (sum of sale price - sum of product cost) / sum of sale price. Give a fraction.",
     f"SELECT (SUM(i.sale_price) - SUM(p.cost)) / SUM(i.sale_price) AS answer FROM {I} i JOIN {P} p "
     f"ON i.product_id = p.id WHERE i.status = 'Complete' AND EXTRACT(YEAR FROM i.created_at) = 2025"),
    ("M6", "medium", "Which customer traffic source generated the most revenue from Complete items ordered in 2025? "
     "Use the traffic source on the customer record. Give the traffic source name.",
     f"SELECT u.traffic_source AS answer FROM {I} i JOIN {U} u ON i.user_id = u.id WHERE i.status = 'Complete' "
     f"AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1 ORDER BY SUM(i.sale_price) DESC LIMIT 1"),
    ("M7", "medium", "How many distinct customers placed at least one order in 2025 that was not Cancelled "
     "(use the order status and order date on the orders table)?",
     f"SELECT COUNT(DISTINCT user_id) AS answer FROM {O} WHERE status != 'Cancelled' AND EXTRACT(YEAR FROM created_at) = 2025"),
    ("M8", "medium", "Which brand sold the most items with status Complete in 2025 (count of order items)? Give the brand name.",
     f"SELECT p.brand AS answer FROM {I} i JOIN {P} p ON i.product_id = p.id WHERE i.status = 'Complete' "
     f"AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1"),
    ("M9", "medium", "For orders delivered in 2025 (orders.delivered_at in 2025), what was the average time from "
     "order placement to delivery, in days (hours divided by 24)?",
     f"SELECT AVG(TIMESTAMP_DIFF(delivered_at, created_at, HOUR) / 24) AS answer FROM {O} "
     f"WHERE EXTRACT(YEAR FROM delivered_at) = 2025"),
    # ---------------- hard: cohorts, windows, comparisons ----------------
    ("H1", "hard", "Of customers whose first non-cancelled order was in 2024, what share placed another non-cancelled "
     "order within 365 days after their first order? Use the orders table. Give a fraction.",
     f"""WITH o AS (SELECT user_id, created_at FROM {O} WHERE status != 'Cancelled'),
     f AS (SELECT user_id, MIN(created_at) first_at FROM o GROUP BY 1)
     SELECT COUNTIF(EXISTS(SELECT 1 FROM o WHERE o.user_id = f.user_id AND o.created_at > f.first_at
       AND o.created_at <= TIMESTAMP_ADD(f.first_at, INTERVAL 365 DAY))) / COUNT(*) AS answer
     FROM f WHERE EXTRACT(YEAR FROM first_at) = 2024"""),
    ("H2", "hard", "What was revenue growth in 2025 versus 2024? Revenue = sum of item sale price excluding Cancelled "
     "and Returned items, by item order date. Growth = 2025 / 2024 - 1, as a fraction.",
     f"SELECT SUM(IF(EXTRACT(YEAR FROM created_at) = 2025, sale_price, 0)) / "
     f"SUM(IF(EXTRACT(YEAR FROM created_at) = 2024, sale_price, 0)) - 1 AS answer FROM {I} WHERE {KEPT}"),
    ("H3", "hard", "Which month of 2025 had the highest revenue? Revenue = sum of item sale price excluding Cancelled "
     "and Returned items, by item order date. Give the month as YYYY-MM.",
     f"SELECT FORMAT_TIMESTAMP('%Y-%m', created_at) AS answer FROM {I} WHERE {KEPT} "
     f"AND EXTRACT(YEAR FROM created_at) = 2025 GROUP BY 1 ORDER BY SUM(sale_price) DESC LIMIT 1"),
    ("H4", "hard", "Which product category had the largest increase in item return rate from 2024 to 2025? Return rate "
     "= Returned items / (Complete + Returned items) by item order year. Only include categories with at least 500 "
     "Complete or Returned items in each year. Give the category name.",
     f"""WITH r AS (SELECT p.category, EXTRACT(YEAR FROM i.created_at) y,
       COUNTIF(i.status = 'Returned') ret, COUNTIF(i.status IN ('Complete', 'Returned')) base
       FROM {I} i JOIN {P} p ON i.product_id = p.id WHERE EXTRACT(YEAR FROM i.created_at) IN (2024, 2025) GROUP BY 1, 2)
     SELECT a.category AS answer FROM r a JOIN r b ON a.category = b.category AND a.y = 2025 AND b.y = 2024
     WHERE a.base >= 500 AND b.base >= 500 ORDER BY a.ret / a.base - b.ret / b.base DESC LIMIT 1"""),
    ("H5", "hard", "What share of 2025 revenue came from customers' first orders? A first order is the customer's "
     "earliest non-cancelled order ever (orders table). Revenue = item sale price excluding Cancelled and Returned "
     "items, ordered in 2025. Give a fraction.",
     f"""WITH firsts AS (SELECT order_id FROM (SELECT order_id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at, order_id) rn
       FROM {O} WHERE status != 'Cancelled') WHERE rn = 1)
     SELECT SUM(IF(order_id IN (SELECT order_id FROM firsts), sale_price, 0)) / SUM(sale_price) AS answer
     FROM {I} WHERE {KEPT} AND EXTRACT(YEAR FROM created_at) = 2025"""),
    ("H6", "hard", "What was the median order value in 2025? Order value = sum of sale price of the order's items that "
     "are not Cancelled or Returned, for items ordered in 2025; include only orders with at least one such item.",
     f"""SELECT ANY_VALUE(m) AS answer FROM (SELECT PERCENTILE_CONT(v, 0.5) OVER () m FROM (
       SELECT order_id, SUM(sale_price) v FROM {I} WHERE {KEPT} AND EXTRACT(YEAR FROM created_at) = 2025 GROUP BY 1))"""),
    ("H7", "hard", "For customers whose first non-cancelled order was in 2024 and who placed a second non-cancelled "
     "order (at any later time), what was the average number of days between the first and second order "
     "(hours divided by 24)? Use the orders table.",
     f"""WITH o AS (SELECT user_id, created_at, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at, order_id) rn
       FROM {O} WHERE status != 'Cancelled')
     SELECT AVG(TIMESTAMP_DIFF(b.created_at, a.created_at, HOUR) / 24) AS answer FROM o a JOIN o b
     ON a.user_id = b.user_id AND a.rn = 1 AND b.rn = 2 WHERE EXTRACT(YEAR FROM a.created_at) = 2024"""),
    ("H8", "hard", "What share of 2025 revenue from Complete items came from the 10 brands with the most such "
     "revenue? Revenue = sum of item sale price for items with status Complete ordered in 2025. Give a fraction.",
     f"""WITH b AS (SELECT p.brand, SUM(i.sale_price) rev FROM {I} i JOIN {P} p ON i.product_id = p.id
       WHERE i.status = 'Complete' AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1)
     SELECT SUM(IF(rk <= 10, rev, 0)) / SUM(rev) AS answer
     FROM (SELECT rev, ROW_NUMBER() OVER (ORDER BY rev DESC) rk FROM b)"""),
]


def main():
    bq = bigquery.Client(project=PROJECT)
    out = []
    for qid, level, question, sql in Q:
        rows = list(bq.query(sql).result())
        value = rows[0].answer
        kind = "text" if isinstance(value, str) else "number"
        out.append({"id": qid, "difficulty": level, "question": question, "reference_sql": " ".join(sql.split()),
                    "answer": value if kind == "text" else float(value), "answer_type": kind, "verified": False})
        print(f"{qid:<3} {value}")
    (ROOT / "eval" / "golden_questions.json").write_text(json.dumps(out, indent=1))

    md = ["# Golden questions: review sheet", "",
          "For each question: read the reference SQL (or paste it into the BigQuery console) and check the answer.",
          "Tick the box when you agree. If the SQL is wrong, note the fix and I will rerun it.", ""]
    for g in out:
        a = g["answer"] if g["answer_type"] == "text" else f"{g['answer']:,.4f}"
        md += [f"## {g['id']} ({g['difficulty']})", "", g["question"], "", f"**Answer:** {a}", "",
               "```sql", g["reference_sql"], "```", "", "- [ ] Verified", ""]
    (ROOT / "eval" / "golden_questions.md").write_text("\n".join(md))


if __name__ == "__main__":
    main()
