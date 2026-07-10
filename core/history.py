# core/history.py
import json
from pathlib import Path

class HistoryManager:
    def __init__(self, history_file_path: str = "data/history.json"):
        self.history_path = Path(history_file_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def save_history(self, rename_pairs: list[tuple[str, str]]):
        """Saving rename history to a JSON file."""
        data = [{"old_path": str(old), "new_path": str(new)} for old, new in rename_pairs]
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_last_history(self) -> list[dict]:
        """Loading the last history if the file exists and is valid."""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def clear_history(self):
        """Clearing the history file after a successful rollback."""
        if self.history_path.exists():
            self.history_path.unlink()