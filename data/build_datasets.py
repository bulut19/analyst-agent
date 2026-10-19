"""Phase 1: build the clean and dirty copies of theLook, plus the answer key.

Run from the project folder:  python data/build_datasets.py

Creates two BigQuery datasets in your project:
  thelook_clean  - a fixed snapshot of 4 theLook tables (orders before CUTOFF)
  thelook_dirty  - the same tables with 40 planted errors (5 of each of 8 types)
and writes data/answer_key.csv listing every planted error.

Everything is deterministic (fixed snapshot date + fixed random seed), so the
same command rebuilds identical tables after the sandbox's 60-day expiry.
Uses only CREATE TABLE AS SELECT (no UPDATE/INSERT), which the sandbox allows.
"""
import csv
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(ROOT / "gcp-key.json"))
if not os.path.isabs(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(ROOT / os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

PROJECT = os.environ["GCP_PROJECT_ID"]
SOURCE = "bigquery-public-data.thelook_ecommerce"
CLEAN = f"{PROJECT}.thelook_clean"
DIRTY = f"{PROJECT}.thelook_dirty"
CUTOFF = "2026-10-01"  # theLook refreshes daily; a fixed cutoff keeps results reproducible
SEED = 42
MAX_BYTES = 2 * 10**9  # hard cap per query (2 GB; these tables are ~45 MB total)

bq = bigquery.Client(project=PROJECT)


def run(sql: str):
    return bq.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES)).result()


def ids(sql: str) -> list:
    return [row[0] for row in run(sql)]


# ---------------------------------------------------------------------------
# 1. Clean snapshot
# ---------------------------------------------------------------------------
def build_clean():
    for name in (CLEAN, DIRTY):
        ds = bigquery.Dataset(name)
        ds.location = "US"
        bq.create_dataset(ds, exists_ok=True)

    run(f"""
    CREATE OR REPLACE TABLE `{CLEAN}.orders` AS
    SELECT * FROM `{SOURCE}.orders` WHERE created_at < TIMESTAMP('{CUTOFF}')""")

    run(f"""
    CREATE OR REPLACE TABLE `{CLEAN}.order_items` AS
    SELECT * FROM `{SOURCE}.order_items`
    WHERE order_id IN (SELECT order_id FROM `{CLEAN}.orders`)""")

    run(f"""
    CREATE OR REPLACE TABLE `{CLEAN}.products` AS
    SELECT * FROM `{SOURCE}.products`""")

    # Drop the geography and street-level columns; nothing in the project needs them.
    run(f"""
    CREATE OR REPLACE TABLE `{CLEAN}.users` AS
    SELECT id, first_name, last_name, email, age, gender, state, city, country,
           postal_code, traffic_source, created_at
    FROM `{SOURCE}.users` WHERE created_at < TIMESTAMP('{CUTOFF}')""")
    print("Clean snapshot built.")


# ---------------------------------------------------------------------------
# 2. Choose rows for each planted error (non-overlapping, seeded)
# ---------------------------------------------------------------------------
def choose_targets():
    rng = random.Random(SEED)
    used_orders = set()

    def pick(pool, k):
        pool = [x for x in pool if x not in used_orders]
        chosen = rng.sample(pool, k)
        used_orders.update(chosen)
        return chosen

    complete = ids(f"SELECT order_id FROM `{CLEAN}.orders` WHERE status = 'Complete' ORDER BY order_id")
    processing = ids(f"SELECT order_id FROM `{CLEAN}.orders` WHERE status = 'Processing' ORDER BY order_id")
    all_orders = ids(f"SELECT order_id FROM `{CLEAN}.orders` ORDER BY order_id")

    t = {
        "duplicate_order": pick(all_orders, 5),
        "missing_user_id": pick(all_orders, 5),
        "delivered_before_created": pick(complete, 5),  # needs a real delivery date
        "outlier_quantity": pick(all_orders, 5),
        "future_order_date": pick(processing, 5),  # not shipped yet, so no other dates conflict
    }

    # Order items from orders not touched above.
    items = run(f"""
        SELECT id, order_id FROM `{CLEAN}.order_items`
        WHERE status = 'Complete' ORDER BY id""")
    item_pool = [(r.id, r.order_id) for r in items if r.order_id not in used_orders]
    chosen_items = rng.sample(item_pool, 10)
    t["invalid_price"] = [i for i, _ in chosen_items[:5]]
    t["orphan_product"] = [i for i, _ in chosen_items[5:]]
    used_orders.update(o for _, o in chosen_items)

    # One product per category variant.
    variants = [("Jeans", "jeans "), ("Jeans", "JEANS"), ("Sweaters", "Sweater"),
                ("Accessories", "Accesories"), ("Tops & Tees", "Tops and Tees")]
    t["inconsistent_category"] = []
    used_products = set()
    for original, variant in variants:
        pool = [p for p in ids(f"SELECT id FROM `{CLEAN}.products` WHERE category = '{original}' ORDER BY id")
                if p not in used_products]
        pid = rng.choice(pool)
        used_products.add(pid)
        t["inconsistent_category"].append((pid, original, variant))
    return t


# ---------------------------------------------------------------------------
# 3. Build the dirty copy and the answer key
# ---------------------------------------------------------------------------
def build_dirty(t):
    key = []  # rows for answer_key.csv

    def add(error_type, table, row_key, column, original, planted, note):
        key.append({"error_id": f"E{len(key) + 1:02d}", "error_type": error_type, "table": table,
                    "row_key": row_key, "column": column, "original_value": original,
                    "planted_value": planted, "description": note})

    def fetch(table, key_col, key_vals, col):
        sql = f"SELECT {key_col} k, CAST({col} AS STRING) v FROM `{CLEAN}.{table}` WHERE {key_col} IN ({','.join(map(str, key_vals))})"
        return {r.k: r.v for r in run(sql)}

    # --- orders ---
    future_dates = ["2027-03-14 10:22:00", "2027-08-02 16:05:00", "2027-11-19 09:41:00",
                    "2028-01-07 13:30:00", "2028-06-25 18:12:00"]
    quantities = [120, 250, 400, 500, 999]
    days_early = [1, 3, 5, 10, 30]

    orig_user = fetch("orders", "order_id", t["missing_user_id"], "user_id")
    orig_created = fetch("orders", "order_id", t["future_order_date"], "created_at")
    orig_items = fetch("orders", "order_id", t["outlier_quantity"], "num_of_item")
    orig_deliv = fetch("orders", "order_id", t["delivered_before_created"], "delivered_at")
    created_for_deliv = fetch("orders", "order_id", t["delivered_before_created"], "created_at")

    user_case = " ".join(f"WHEN {o} THEN NULL" for o in t["missing_user_id"])
    created_case = " ".join(f"WHEN {o} THEN TIMESTAMP('{d}')" for o, d in zip(t["future_order_date"], future_dates))
    items_case = " ".join(f"WHEN {o} THEN {q}" for o, q in zip(t["outlier_quantity"], quantities))
    deliv_case = " ".join(f"WHEN {o} THEN TIMESTAMP_SUB(created_at, INTERVAL {d} DAY)"
                          for o, d in zip(t["delivered_before_created"], days_early))
    dup_list = ",".join(map(str, t["duplicate_order"]))

    run(f"""
    CREATE OR REPLACE TABLE `{DIRTY}.orders` AS
    WITH modified AS (
      SELECT * REPLACE (
        CASE order_id {user_case} ELSE user_id END AS user_id,
        CASE order_id {created_case} ELSE created_at END AS created_at,
        CASE order_id {items_case} ELSE num_of_item END AS num_of_item,
        CASE order_id {deliv_case} ELSE delivered_at END AS delivered_at)
      FROM `{CLEAN}.orders`)
    SELECT * FROM modified
    UNION ALL
    SELECT * FROM modified WHERE order_id IN ({dup_list})""")

    for o in t["duplicate_order"]:
        add("duplicate_order", "orders", f"order_id={o}", "(entire row)", "1 row", "2 identical rows",
            "Same order recorded twice")
    for o in t["missing_user_id"]:
        add("missing_user_id", "orders", f"order_id={o}", "user_id", orig_user[o], "NULL",
            "Order has no customer ID")
    for o, d in zip(t["delivered_before_created"], days_early):
        add("delivered_before_created", "orders", f"order_id={o}", "delivered_at", orig_deliv[o],
            f"{d} day(s) before created_at ({created_for_deliv[o]})", "Delivery date is earlier than the order date")
    for o, q in zip(t["outlier_quantity"], quantities):
        add("outlier_quantity", "orders", f"order_id={o}", "num_of_item", orig_items[o], q,
            "Item count far above the normal maximum of 4")
    for o, d in zip(t["future_order_date"], future_dates):
        add("future_order_date", "orders", f"order_id={o}", "created_at", orig_created[o], d,
            "Order date is in the future")

    # --- order_items ---
    prices = [0.0, 0.0, -19.99, -45.5, -120.0]
    orphan_ids = [30001, 30002, 30003, 30004, 30005]  # products.id ends at 29120
    orig_price = fetch("order_items", "id", t["invalid_price"], "sale_price")
    orig_prod = fetch("order_items", "id", t["orphan_product"], "product_id")

    price_case = " ".join(f"WHEN {i} THEN {p}" for i, p in zip(t["invalid_price"], prices))
    prod_case = " ".join(f"WHEN {i} THEN {p}" for i, p in zip(t["orphan_product"], orphan_ids))
    run(f"""
    CREATE OR REPLACE TABLE `{DIRTY}.order_items` AS
    SELECT * REPLACE (
      CASE id {price_case} ELSE sale_price END AS sale_price,
      CASE id {prod_case} ELSE product_id END AS product_id)
    FROM `{CLEAN}.order_items`""")

    for i, p in zip(t["invalid_price"], prices):
        add("invalid_price", "order_items", f"id={i}", "sale_price", orig_price[i], p,
            "Sale price is zero or negative")
    for i, p in zip(t["orphan_product"], orphan_ids):
        add("orphan_product", "order_items", f"id={i}", "product_id", orig_prod[i], p,
            "Product ID does not exist in products")

    # --- products ---
    cat_case = " ".join(f"WHEN {pid} THEN '{variant}'" for pid, _, variant in t["inconsistent_category"])
    run(f"""
    CREATE OR REPLACE TABLE `{DIRTY}.products` AS
    SELECT * REPLACE (CASE id {cat_case} ELSE category END AS category)
    FROM `{CLEAN}.products`""")
    for pid, original, variant in t["inconsistent_category"]:
        add("inconsistent_category", "products", f"id={pid}", "category", original, repr(variant),
            "Category spelled differently from the standard value")

    # --- users (unchanged) ---
    run(f"CREATE OR REPLACE TABLE `{DIRTY}.users` AS SELECT * FROM `{CLEAN}.users`")

    out = ROOT / "data" / "answer_key.csv"
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(key[0].keys()))
        writer.writeheader()
        writer.writerows(key)
    print(f"Dirty copy built. {len(key)} planted errors written to {out.relative_to(ROOT)}")


def summary():
    for ds in (CLEAN, DIRTY):
        print(f"\n{ds.split('.')[-1]}")
        for table in ("orders", "order_items", "products", "users"):
            n = list(run(f"SELECT COUNT(*) n FROM `{ds}.{table}`"))[0].n
            print(f"  {table:<12} {n:>9,} rows")


if __name__ == "__main__":
    build_clean()
    build_dirty(choose_targets())
    summary()
