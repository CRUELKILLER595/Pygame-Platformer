
import os
import re

# Use a headless Pygame display for generating previews.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pathlib import Path

import pygame

from pixelbound_core.assets import (
    AssetCatalog,
    AssetDefinition,
)

from pixelbound_core.assets.catalog_io import save_asset_catalog

from pixelbound_core.config.paths import (
    PROJECT_ROOT,
    CONTENT_DIR,
)


# --------------------------------------------------
# OUTPUT PATHS
# --------------------------------------------------

PREVIEW_DIR = CONTENT_DIR / "asset_previews"

CATALOG_PATH = CONTENT_DIR / "asset_catalog.json"


# --------------------------------------------------
# SEMANTIC ROLES
# --------------------------------------------------

CLASS_ROLES = {
    "Player": "player_spawn",
    "Block": "terrain",
    "Fire": "hazard",
    "Checkpoint": "checkpoint",
    "Start": "level_start",
    "End": "level_end",
    "Fruit": "collectible",
    "Box": "breakable",
    "Trap": "hazard",
    "Enemy": "enemy",
}


CATEGORY_ROLES = {
    "TILES": "terrain",
    "CHARACTERS": "player_spawn",
    "ENEMIES": "enemy",
    "TRAPS": "hazard",
    "BREAKABLES": "breakable",
    "COLLECTIBLES": "collectible",
    "LEVEL": "level_object",
    "BACKGROUNDS": "background",
    "EFFECTS": "effect",
}


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_asset_role(asset):

    object_class = getattr(
        asset,
        "object_class",
        None,
    )

    class_name = getattr(
        object_class,
        "__name__",
        None,
    )

    return (
        CLASS_ROLES.get(class_name)
        or CATEGORY_ROLES.get(asset.category)
        or "generic"
    )


def get_animation_specs(asset):

    specs = {}

    animations = getattr(
        asset,
        "animations",
        {},
    ) or {}

    for animation_name, frames in animations.items():

        frames = list(frames or [])

        if not frames:
            continue

        specs[animation_name] = {
            "frame_count": len(frames),
            "frame_size": list(frames[0].get_size()),
        }

    return specs


def save_preview(image, asset_id, suffix=""):

    if not isinstance(image, pygame.Surface):
        raise TypeError(
            f"Asset {asset_id} has no valid preview Surface."
        )

    safe_id = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        asset_id,
    )

    if safe_id != asset_id:
        raise ValueError(
            f"Unsafe asset ID for preview: {asset_id}"
        )

    filename = f"{safe_id}{suffix}.png"

    output_path = PREVIEW_DIR / filename

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pygame.image.save(
        image,
        str(output_path),
    )

    return output_path.relative_to(
        PROJECT_ROOT
    ).as_posix()


# --------------------------------------------------
# CONVERSION
# --------------------------------------------------

def convert_runtime_asset(asset):

    preview_path = save_preview(
        asset.image,
        asset.id,
    )

    metadata = {}

    # Preserve useful enemy metadata.
    if hasattr(asset, "enemy_id"):
        metadata["enemy_id"] = asset.enemy_id

    if hasattr(asset, "lethal"):
        metadata["lethal"] = bool(asset.lethal)

    # Preserve the default preview animation.
    if hasattr(asset, "preview_animation"):
        metadata["preview_animation"] = (
            asset.preview_animation
        )

    # Export the pressed state of the End asset, if present.
    pressed_image = getattr(
        asset,
        "pressed_image",
        None,
    )

    if isinstance(pressed_image, pygame.Surface):

        metadata["pressed_preview_path"] = save_preview(
            pressed_image,
            asset.id,
            suffix="_pressed",
        )

    return AssetDefinition(
        id=asset.id,
        name=asset.name,
        category=asset.category,
        width=asset.width,
        height=asset.height,
        preview_path=preview_path,
        role=get_asset_role(asset),
        score_value=int(
            getattr(asset, "score_value", 0)
        ),
        profile=dict(
            getattr(asset, "profile", {}) or {}
        ),
        animation_specs=get_animation_specs(asset),
        metadata=metadata,
    )


# --------------------------------------------------
# BUILD CATALOG
# --------------------------------------------------

def build_catalog():

    from game.systems.asset_manager import AssetManager

    pygame.display.init()
    pygame.display.set_mode((1, 1))

    try:

        PREVIEW_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        manager = AssetManager()

        runtime_assets = manager.load_all()

        catalog = AssetCatalog()

        for asset in runtime_assets.values():

            definition = convert_runtime_asset(asset)

            catalog.register(definition)

        save_asset_catalog(
            catalog,
            CATALOG_PATH,
        )

        print("\nCATALOG BUILD COMPLETE")

        print("Total assets:", len(catalog))

        for category in catalog.get_categories():

            print(
                category,
                ":",
                len(catalog.get_by_category(category)),
            )

        return catalog

    finally:
        pygame.quit()


if __name__ == "__main__":
    build_catalog()
