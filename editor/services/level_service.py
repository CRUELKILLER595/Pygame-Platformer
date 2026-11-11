
"""Translate between PixelBound Core levels and Editor assets."""

from pathlib import Path

from pixelbound_core.levels import (
    create_empty_level,
    load_level_data,
    save_level_data,
)


class EditorLevelService:

    def __init__(self, asset_library):
        self.asset_library = asset_library

    # ------------------------------------------
    # LOAD
    # ------------------------------------------

    def load_level(self, level_path):

        level_path = Path(level_path)

        if level_path.is_file():

            level_data = load_level_data(level_path)

        else:

            level_data = create_empty_level(
                level_path.stem
            )

        placed_assets = {}
        missing_assets = []

        for index, record in enumerate(
            level_data.get("objects", [])
        ):

            if not isinstance(record, dict):
                missing_assets.append(
                    f"Malformed object at index {index}"
                )
                continue

            asset_id = record.get("id")

            if not isinstance(asset_id, str):
                missing_assets.append(
                    f"Invalid asset ID at index {index}"
                )
                continue

            try:
                position = (
                    int(record["x"]),
                    int(record["y"]),
                )
            except (KeyError, TypeError, ValueError):
                missing_assets.append(
                    f"Invalid coordinates for {asset_id}"
                )
                continue

            asset = self.asset_library.get(asset_id)

            if asset is None:

                missing_assets.append(asset_id)
                continue

            placed_assets[position] = asset

        if missing_assets:
            print(
                "EDITOR: Missing or invalid level objects:",
                missing_assets,
            )

        return level_data, placed_assets

    # ------------------------------------------
    # SAVE
    # ------------------------------------------

    def save_level(
        self,
        level_path,
        level_data,
        placed_assets,
    ):

        level_data = dict(level_data)

        level_data["objects"] = [
            {
                "id": asset.id,
                "x": int(position[0]),
                "y": int(position[1]),
            }
            for position, asset in placed_assets.items()
        ]

        return save_level_data(
            level_path,
            level_data,
        )
