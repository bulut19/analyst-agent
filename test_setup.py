"""Phase 0 check: one BigQuery query and one Claude call."""
import os
from dotenv import load_dotenv
from google.cloud import bigquery
import anthropic

load_dotenv()
PROJECT = os.environ["GCP_PROJECT_ID"]
DATASET = os.environ.get("BQ_DATASET", "analyst_agent")

# 1. BigQuery: dry run first (cost check), then run with a hard cap.
bq = bigquery.Client(project=PROJECT)
sql = "SELECT COUNT(*) AS orders FROM `bigquery-public-data.thelook_ecommerce.orders`"
dry = bq.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
print(f"BigQuery dry run: {dry.total_bytes_processed / 1e6:.1f} MB would be scanned")
job = bq.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=10**9))
print(f"BigQuery OK: theLook has {list(job.result())[0].orders:,} orders")

# Create our own dataset (tests the Data Editor role).
ds = bigquery.Dataset(f"{PROJECT}.{DATASET}")
ds.location = "US"
bq.create_dataset(ds, exists_ok=True)
print(f"BigQuery OK: dataset {DATASET} is ready")

# 2. Claude: find the newest Sonnet model, then send one message.
claude = anthropic.Anthropic()
sonnets = [m.id for m in claude.models.list(limit=50) if "sonnet" in m.id]
model = os.environ.get("CLAUDE_MODEL") or sonnets[0]
reply = claude.messages.create(
    model=model,
    max_tokens=50,
    messages=[{"role": "user", "content": "Reply with exactly: Setup works."}],
)
print(f"Claude OK ({model}): {reply.content[0].text}")
print("\nPhase 0 complete.")
