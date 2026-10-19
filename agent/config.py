"""Shared settings: loads .env, points Google at the key file, defines models and datasets."""
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

_cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "gcp-key.json")
_cred = _cred if os.path.isabs(_cred) else str(ROOT / _cred)
if not Path(_cred).exists() and os.environ.get("GCP_SERVICE_ACCOUNT_JSON"):  # hosted app: key comes from secrets
    _cred = str(Path(tempfile.gettempdir()) / "gcp-key.json")
    Path(_cred).write_text(os.environ["GCP_SERVICE_ACCOUNT_JSON"])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _cred

PROJECT = os.environ["GCP_PROJECT_ID"]
CLEAN_DATASET = f"{PROJECT}.thelook_clean"
DIRTY_DATASET = f"{PROJECT}.thelook_dirty"
ACTIVE_DATASET = os.environ.get("ACTIVE_DATASET", DIRTY_DATASET)  # the agent works on the dirty copy by default

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")        # main agent
FAST_MODEL = os.environ.get("CLAUDE_FAST_MODEL", "claude-haiku-5-5")  # stakeholder simulator, cheap tasks

MAX_QUESTIONS = 5                 # requirements interview limit
MAX_BYTES_BILLED = 2 * 10**9      # hard cap per BigQuery query

PROMPTS = ROOT / "prompts"
OUTPUTS = ROOT / "outputs"


def prompt(name: str) -> str:
    """Load a prompt file from prompts/."""
    return (PROMPTS / f"{name}.md").read_text()
