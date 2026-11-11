
import json
from pathlib import Path


DEFAULT_LEVEL_PATH = Path("levels/level1.json")


def save_level(
    level_data,
    placed_assets,
    level_path=DEFAULT_LEVEL_PATH
):
    level_path = Path(level_path)

    print("SAVING:", level_path)

    # Store all placed objects.
    level_data["objects"] = []

    for (x, y), asset in placed_assets.items():
        object_data = {
            "id": asset.id,
            "x": int(x),
            "y": int(y)
        }

        level_data["objects"].append(object_data)

    # Use one consistent soundtrack field name.
    if "soundtrack" not in level_data:
        level_data["soundtrack"] = (
            level_data.get("soundtracks", "")
        )

    level_data.pop("soundtracks", None)

    # Create the levels directory if needed.
    level_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with level_path.open("w", encoding="utf-8") as file:
        json.dump(level_data, file, indent=4)

    print("File saved successfully:", level_path)


def load_level(
    ASSETS,
    level_path=DEFAULT_LEVEL_PATH
):
    level_path = Path(level_path)

    placed_assets = {}

    if not level_path.is_file():
        print("Level file not found:", level_path)
        return placed_assets

    with level_path.open("r", encoding="utf-8") as file:
        level_data = json.load(file)

    for object_data in level_data.get("objects", []):
        asset_id = object_data["id"]

        x = int(object_data["x"])
        y = int(object_data["y"])

        asset = ASSETS.get(asset_id)

        if asset is None:
            print("Asset not found:", asset_id)
            continue

        placed_assets[(x, y)] = asset

    return placed_assets
