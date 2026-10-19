# Golden questions: review sheet

For each question: read the reference SQL (or paste it into the BigQuery console) and check the answer.
Tick the box when you agree. If the SQL is wrong, note the fix and I will rerun it.

**Preliminary run (before your review): the agent got 24/25.** The one miss, M9, was a problem with the test:
the reference SQL counted whole hours. Decision: use exact elapsed time. M9 now says so, and its reference
uses seconds, which matches the agent's original answer (3.989 days).

## E1 (easy)

How many orders were placed in calendar year 2025 (any status)?

**Answer:** 28,819.0000

```sql
SELECT COUNT(*) AS answer FROM `analyst-agent-512103.thelook_clean.orders` WHERE EXTRACT(YEAR FROM created_at) = 2025
```

- [x] Verified (Melisa)

## E2 (easy)

How many customers signed up through the Facebook traffic source?

**Answer:** 5,777.0000

```sql
SELECT COUNT(*) AS answer FROM `analyst-agent-512103.thelook_clean.users` WHERE traffic_source = 'Facebook'
```

- [x] Verified (Melisa)

## E3 (easy)

What share of all orders have the status Cancelled? Give a fraction between 0 and 1.

**Answer:** 0.1494

```sql
SELECT COUNTIF(status = 'Cancelled') / COUNT(*) AS answer FROM `analyst-agent-512103.thelook_clean.orders`
```

- [x] Verified (Melisa)

## E4 (easy)

What is the average age of all customers?

**Answer:** 40.8959

```sql
SELECT AVG(age) AS answer FROM `analyst-agent-512103.thelook_clean.users`
```

- [x] Verified (Melisa)

## E5 (easy)

How many distinct brands are in the product catalog (ignore missing brands)?

**Answer:** 2,756.0000

```sql
SELECT COUNT(DISTINCT brand) AS answer FROM `analyst-agent-512103.thelook_clean.products` WHERE brand IS NOT NULL
```

- [x] Verified (Melisa)

## E6 (easy)

What is the average retail (list) price of products in the Jeans category?

**Answer:** 97.8532

```sql
SELECT AVG(retail_price) AS answer FROM `analyst-agent-512103.thelook_clean.products` WHERE category = 'Jeans'
```

- [x] Verified (Melisa)

## E7 (easy)

Which country has the most customers? Give the country name.

**Answer:** China

```sql
SELECT country AS answer FROM `analyst-agent-512103.thelook_clean.users` GROUP BY country ORDER BY COUNT(*) DESC LIMIT 1
```

- [x] Verified (Melisa)

## E8 (easy)

What is the total sale price of order items with status Complete that were ordered in 2025?

**Answer:** 614,334.4905

```sql
SELECT SUM(sale_price) AS answer FROM `analyst-agent-512103.thelook_clean.order_items` WHERE status = 'Complete' AND EXTRACT(YEAR FROM created_at) = 2025
```

- [x] Verified (Melisa)

## M1 (medium)

What was 2025 revenue from the Women's department? Revenue = sum of order item sale price, excluding items with status Cancelled or Returned; use the item's order date (order_items.created_at).

**Answer:** 859,153.1709

```sql
SELECT SUM(i.sale_price) AS answer FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.products` p ON i.product_id = p.id WHERE p.department = 'Women' AND i.status NOT IN ('Cancelled', 'Returned') AND EXTRACT(YEAR FROM i.created_at) = 2025
```

- [x] Verified (Melisa)

## M2 (medium)

Which product category had the highest revenue in 2025? Revenue = sum of item sale price, excluding Cancelled and Returned items, by item order date. Give the category name.

**Answer:** Outerwear & Coats

```sql
SELECT p.category AS answer FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.products` p ON i.product_id = p.id WHERE i.status NOT IN ('Cancelled', 'Returned') AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1 ORDER BY SUM(i.sale_price) DESC LIMIT 1
```

- [x] Verified (Melisa)

## M3 (medium)

What was the average order value in 2025? Order value = sum of sale price of the order's items that are not Cancelled or Returned; include only orders with at least one such item; use item order dates in 2025.

**Answer:** 85.7184

```sql
SELECT AVG(v) AS answer FROM (SELECT order_id, SUM(sale_price) v FROM `analyst-agent-512103.thelook_clean.order_items` WHERE status NOT IN ('Cancelled', 'Returned') AND EXTRACT(YEAR FROM created_at) = 2025 GROUP BY 1)
```

- [x] Verified (Melisa)

## M4 (medium)

What was the item return rate in 2025? Return rate = items with status Returned divided by items with status Complete or Returned, for items ordered in 2025. Give a fraction.

**Answer:** 0.2952

```sql
SELECT COUNTIF(status = 'Returned') / COUNTIF(status IN ('Complete', 'Returned')) AS answer FROM `analyst-agent-512103.thelook_clean.order_items` WHERE EXTRACT(YEAR FROM created_at) = 2025
```

- [x] Verified (Melisa)

## M5 (medium)

What was the gross margin percentage in 2025 for items with status Complete? Gross margin % = (sum of sale price - sum of product cost) / sum of sale price. Give a fraction.

**Answer:** 0.5198

```sql
SELECT (SUM(i.sale_price) - SUM(p.cost)) / SUM(i.sale_price) AS answer FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.products` p ON i.product_id = p.id WHERE i.status = 'Complete' AND EXTRACT(YEAR FROM i.created_at) = 2025
```

- [x] Verified (Melisa)

## M6 (medium)

Which customer traffic source generated the most revenue from Complete items ordered in 2025? Use the traffic source on the customer record. Give the traffic source name.

**Answer:** Search

```sql
SELECT u.traffic_source AS answer FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.users` u ON i.user_id = u.id WHERE i.status = 'Complete' AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1 ORDER BY SUM(i.sale_price) DESC LIMIT 1
```

- [x] Verified (Melisa)

## M7 (medium)

How many distinct customers placed at least one order in 2025 that was not Cancelled (use the order status and order date on the orders table)?

**Answer:** 21,468.0000

```sql
SELECT COUNT(DISTINCT user_id) AS answer FROM `analyst-agent-512103.thelook_clean.orders` WHERE status != 'Cancelled' AND EXTRACT(YEAR FROM created_at) = 2025
```

- [x] Verified (Melisa)

## M8 (medium)

Which brand sold the most items with status Complete in 2025 (count of order items)? Give the brand name.

**Answer:** Allegra K

```sql
SELECT p.brand AS answer FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.products` p ON i.product_id = p.id WHERE i.status = 'Complete' AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1
```

- [x] Verified (Melisa)

## M9 (medium)

For orders delivered in 2025 (orders.delivered_at in 2025), what was the average time from order placement to delivery, in days, using the exact elapsed time (to the second)?

**Answer:** 3.9888

```sql
SELECT AVG(TIMESTAMP_DIFF(delivered_at, created_at, SECOND) / 86400) AS answer FROM `analyst-agent-512103.thelook_clean.orders` WHERE EXTRACT(YEAR FROM delivered_at) = 2025
```

- [x] Verified (Melisa)

## H1 (hard)

Of customers whose first non-cancelled order was in 2024, what share placed another non-cancelled order within 365 days after their first order? Use the orders table. Give a fraction.

**Answer:** 0.1928

```sql
WITH o AS (SELECT user_id, created_at FROM `analyst-agent-512103.thelook_clean.orders` WHERE status != 'Cancelled'), f AS (SELECT user_id, MIN(created_at) first_at FROM o GROUP BY 1) SELECT COUNTIF(EXISTS(SELECT 1 FROM o WHERE o.user_id = f.user_id AND o.created_at > f.first_at AND o.created_at <= TIMESTAMP_ADD(f.first_at, INTERVAL 365 DAY))) / COUNT(*) AS answer FROM f WHERE EXTRACT(YEAR FROM first_at) = 2024
```

- [x] Verified (Melisa)

## H2 (hard)

What was revenue growth in 2025 versus 2024? Revenue = sum of item sale price excluding Cancelled and Returned items, by item order date. Growth = 2025 / 2024 - 1, as a fraction.

**Answer:** 0.4716

```sql
SELECT SUM(IF(EXTRACT(YEAR FROM created_at) = 2025, sale_price, 0)) / SUM(IF(EXTRACT(YEAR FROM created_at) = 2024, sale_price, 0)) - 1 AS answer FROM `analyst-agent-512103.thelook_clean.order_items` WHERE status NOT IN ('Cancelled', 'Returned')
```

- [x] Verified (Melisa)

## H3 (hard)

Which month of 2025 had the highest revenue? Revenue = sum of item sale price excluding Cancelled and Returned items, by item order date. Give the month as YYYY-MM.

**Answer:** 2025-12

```sql
SELECT FORMAT_TIMESTAMP('%Y-%m', created_at) AS answer FROM `analyst-agent-512103.thelook_clean.order_items` WHERE status NOT IN ('Cancelled', 'Returned') AND EXTRACT(YEAR FROM created_at) = 2025 GROUP BY 1 ORDER BY SUM(sale_price) DESC LIMIT 1
```

- [x] Verified (Melisa)

## H4 (hard)

Which product category had the largest increase in item return rate from 2024 to 2025? Return rate = Returned items / (Complete + Returned items) by item order year. Only include categories with at least 500 Complete or Returned items in each year. Give the category name.

**Answer:** Jeans

```sql
WITH r AS (SELECT p.category, EXTRACT(YEAR FROM i.created_at) y, COUNTIF(i.status = 'Returned') ret, COUNTIF(i.status IN ('Complete', 'Returned')) base FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.products` p ON i.product_id = p.id WHERE EXTRACT(YEAR FROM i.created_at) IN (2024, 2025) GROUP BY 1, 2) SELECT a.category AS answer FROM r a JOIN r b ON a.category = b.category AND a.y = 2025 AND b.y = 2024 WHERE a.base >= 500 AND b.base >= 500 ORDER BY a.ret / a.base - b.ret / b.base DESC LIMIT 1
```

- [x] Verified (Melisa)

## H5 (hard)

What share of 2025 revenue came from customers' first orders? A first order is the customer's earliest non-cancelled order ever (orders table). Revenue = item sale price excluding Cancelled and Returned items, ordered in 2025. Give a fraction.

**Answer:** 0.6525

```sql
WITH firsts AS (SELECT order_id FROM (SELECT order_id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at, order_id) rn FROM `analyst-agent-512103.thelook_clean.orders` WHERE status != 'Cancelled') WHERE rn = 1) SELECT SUM(IF(order_id IN (SELECT order_id FROM firsts), sale_price, 0)) / SUM(sale_price) AS answer FROM `analyst-agent-512103.thelook_clean.order_items` WHERE status NOT IN ('Cancelled', 'Returned') AND EXTRACT(YEAR FROM created_at) = 2025
```

- [x] Verified (Melisa)

## H6 (hard)

What was the median order value in 2025? Order value = sum of sale price of the order's items that are not Cancelled or Returned, for items ordered in 2025; include only orders with at least one such item.

**Answer:** 55.0000

```sql
SELECT ANY_VALUE(m) AS answer FROM (SELECT PERCENTILE_CONT(v, 0.5) OVER () m FROM ( SELECT order_id, SUM(sale_price) v FROM `analyst-agent-512103.thelook_clean.order_items` WHERE status NOT IN ('Cancelled', 'Returned') AND EXTRACT(YEAR FROM created_at) = 2025 GROUP BY 1))
```

- [x] Verified (Melisa)

## H7 (hard)

For customers whose first non-cancelled order was in 2024 and who placed a second non-cancelled order (at any later time), what was the average number of days between the first and second order (hours divided by 24)? Use the orders table.

**Answer:** 360.1843

```sql
WITH o AS (SELECT user_id, created_at, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at, order_id) rn FROM `analyst-agent-512103.thelook_clean.orders` WHERE status != 'Cancelled') SELECT AVG(TIMESTAMP_DIFF(b.created_at, a.created_at, HOUR) / 24) AS answer FROM o a JOIN o b ON a.user_id = b.user_id AND a.rn = 1 AND b.rn = 2 WHERE EXTRACT(YEAR FROM a.created_at) = 2024
```

- [x] Verified (Melisa)

## H8 (hard)

What share of 2025 revenue from Complete items came from the 10 brands with the most such revenue? Revenue = sum of item sale price for items with status Complete ordered in 2025. Give a fraction.

**Answer:** 0.1478

```sql
WITH b AS (SELECT p.brand, SUM(i.sale_price) rev FROM `analyst-agent-512103.thelook_clean.order_items` i JOIN `analyst-agent-512103.thelook_clean.products` p ON i.product_id = p.id WHERE i.status = 'Complete' AND EXTRACT(YEAR FROM i.created_at) = 2025 GROUP BY 1) SELECT SUM(IF(rk <= 10, rev, 0)) / SUM(rev) AS answer FROM (SELECT rev, ROW_NUMBER() OVER (ORDER BY rev DESC) rk FROM b)
```

- [x] Verified (Melisa)
