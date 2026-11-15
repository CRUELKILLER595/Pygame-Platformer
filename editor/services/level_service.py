"""Translate between PixelBound Core levels and Editor assets."""

from pathlib import Path

from pixelbound_core.config.paths import LEVELS_DIR

from pixelbound_core.levels import (
    create_empty_level,
    generate_level_id,
    load_level_data,
    save_level_data,
)


class EditorLevelService:

    def __init__(self, asset_library):
        self.asset_library = asset_library

    # ==========================================
    # CREATE LEVEL
    # ==========================================

    def create_level(self, level_name, levels_dir=LEVELS_DIR):
        """
        Create a new empty level and save it locally.

        The level receives:
            - A unique level ID
            - A display name
            - A new JSON file
            - The default PixelBound level structure
        """

        if not isinstance(level_name, str):
            raise ValueError("Level name must be text.")

        level_name = level_name.strip()

        if not level_name:
            raise ValueError("Please enter a level name.")

        if len(level_name) > 60:
            raise ValueError(
                "Level name must be 60 characters or fewer."
            )

        levels_dir = Path(levels_dir)

        levels_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Generate a unique ID.
        for _ in range(10):

            level_id = generate_level_id()

            level_path = levels_dir / f"{level_id}.json"

            if not level_path.exists():
                break

        else:
            raise RuntimeError(
                "Could not allocate a unique level ID. Try again."
            )

        # Create the default level structure.
        level_data = create_empty_level(level_name)

        # Store the stable identity inside the JSON.
        level_data["level_id"] = level_id

        # Use the existing shared serializer.
        return save_level_data(
            level_path,
            level_data,
        )

    # ==========================================
    # LOAD LEVEL
    # ==========================================

    def load_level(self, level_path):

        level_path = Path(level_path)

        if level_path.is_file():

            level_data = load_level_data(level_path)

        else:

            level_data = create_empty_level(
                level_path.stem
            )

        # Older levels do not have level_id.
        # Use their existing filename as their identity.
        level_data.setdefault(
            "level_id",
            level_path.stem,
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

    # ==========================================
    # SAVE LEVEL
    # ==========================================

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