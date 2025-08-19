import json
from pathlib import Path
from typing import Dict


def load_json(filepath: str) -> dict:
    """
    Read a JSON file and return a dictionary object.
    Raises an exception if the file does not exist or the JSON is malformed.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"❌ File not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def save_json(data: Dict, path: str | Path) -> None:
    """Serialize `data` to JSON and save; ensure UTF-8 and readable indentation."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


import difflib
from typing import List, Optional


def closest_match(target: str, candidates: List[str]) -> Optional[str]:
    """
    Return the string in `candidates` that is most similar to `target`.
    """
    # n=1: take only the best match; cutoff=0 ensures a result as long as candidates is not empty
    matches = difflib.get_close_matches(target, candidates, n=1, cutoff=0)
    return matches[0] if matches else None
