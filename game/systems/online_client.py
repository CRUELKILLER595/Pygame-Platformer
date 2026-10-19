import requests
import json
import re
from pathlib import Path
API_BASE_URL = "http://127.0.0.1:8000"
def fetch_level_catalog():
    response = requests.get(
        f"{API_BASE_URL}/levels/catalog",
        timeout=5,
    )
    response.raise_for_status()

    return response.json().get("levels", [])
def download_level_to_cache(level_id):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", level_id):
        raise ValueError("Invalid level ID")

    response = requests.get(
        f"{API_BASE_URL}/levels/{level_id}/data",
        timeout=10,
    )
    response.raise_for_status()

    payload = response.json()
    level_data = payload["level_data"]

    project_root = Path(__file__).resolve().parents[2]
    cache_dir = project_root / "cache" / "online_levels"
    cache_dir.mkdir(parents=True, exist_ok=True)

    level_path = cache_dir / f"{level_id}.json"

    with level_path.open("w", encoding="utf-8") as file:
        json.dump(level_data, file, indent=2)

    return str(level_path)
def fetch_next_playable_level(current_level_id):
    levels = [
        level
        for level in fetch_level_catalog()
        if level.get("playable", False)
    ]

    def sort_key(level):
        match = re.search(r"\d+", level["id"])
        return int(match.group()) if match else float("inf")

    levels.sort(key=sort_key)

    for index, level in enumerate(levels):
        if level["id"] == current_level_id:
            if index + 1 < len(levels):
                return levels[index + 1]
            return None

    return None