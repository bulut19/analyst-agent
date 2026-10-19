"""The shared project state: one JSON file per run that every stage reads and writes."""
import json
import time
from pathlib import Path

from agent.config import OUTPUTS


class ProjectState(dict):
    """A dict saved to outputs/runs/<run_id>/state.json after every change."""

    def __init__(self, run_id=None, **data):
        super().__init__(data)
        self.run_id = run_id or time.strftime("%Y%m%d-%H%M%S")
        self.path = OUTPUTS / "runs" / self.run_id / "state.json"

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self, indent=2, default=str))
        return self

    def set(self, key, value):
        self[key] = value
        return self.save()

    @classmethod
    def load(cls, run_id):
        path = OUTPUTS / "runs" / run_id / "state.json"
        return cls(run_id, **json.loads(Path(path).read_text()))
