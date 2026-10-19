"""Check that each planted error type appears 5 times in the dirty copy and 0 times in the clean copy.

Run from the project folder:  python data/verify_datasets.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "gcp-key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred if os.path.isabs(cred) else str(ROOT / cred)
PROJECT = os.environ["GCP_PROJECT_ID"]
bq = bigquery.Client(project=PROJECT)

CHECKS = {
    "duplicate_order": "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM `{ds}.orders`",
    "missing_user_id": "SELECT COUNTIF(user_id IS NULL) FROM `{ds}.orders`",
    "delivered_before_created": "SELECT COUNTIF(delivered_at < created_at) FROM `{ds}.orders`",
    "outlier_quantity": "SELECT COUNTIF(num_of_item > 4) FROM `{ds}.orders`",
    "future_order_date": "SELECT COUNTIF(created_at > TIMESTAMP('2026-10-01')) FROM `{ds}.orders`",
    "invalid_price": "SELECT COUNTIF(sale_price <= 0) FROM `{ds}.order_items`",
    "orphan_product": "SELECT COUNTIF(p.id IS NULL) FROM `{ds}.order_items` i LEFT JOIN `{ds}.products` p ON i.product_id = p.id",
    "inconsistent_category": "SELECT COUNTIF(category IN ('jeans ', 'JEANS', 'Sweater', 'Accesories', 'Tops and Tees')) FROM `{ds}.products`",
}

print(f"{'error type':<26}{'clean':>7}{'dirty':>7}")
ok = True
for name, sql in CHECKS.items():
    counts = []
    for ds in ("thelook_clean", "thelook_dirty"):
        q = sql.format(ds=f"{PROJECT}.{ds}")
        counts.append(list(bq.query(q).result())[0][0])
    ok &= counts == [0, 5]
    print(f"{name:<26}{counts[0]:>7}{counts[1]:>7}")
print("\nAll 8 error types planted correctly." if ok else "\nMISMATCH: check the rows above.")
