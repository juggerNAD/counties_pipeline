from pathlib import Path
import json

CHECKPOINT_FILE = Path("data/checkpoint.json")

def save_checkpoint(case_id: str):
    """
    Save the last processed case ID for resuming scraper.
    """
    checkpoint_data = {"last_case": case_id}
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint_data))

def load_checkpoint() -> str:
    """
    Load the last processed case ID. Returns None if not exists.
    """
    if not CHECKPOINT_FILE.exists():
        return None
    data = json.loads(CHECKPOINT_FILE.read_text())
    return data.get("last_case")
