
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pygame

from pixelbound_core.assets.asset_catalog import AssetCatalog
from pixelbound_core.assets.asset_definition import AssetDefinition
from pixelbound_core.config.paths import PROJECT_ROOT


@dataclass
class EditorAsset:
    """
    Editor-side representation of an asset.

    Contains a preview image and shared asset metadata.
    Does not contain Game runtime classes.
    """

    definition: AssetDefinition
    image: pygame.Surface

    @property
    def id(self):
        return self.definition.id

    @property
    def name(self):
        return self.definition.name

    @property
    def category(self):
        return self.definition.category

    @property
    def width(self):
        return self.definition.width

    @property
    def height(self):
        return self.definition.height

    @property
    def role(self):
        return self.definition.role

    @property
    def score_value(self):
        return self.definition.score_value

    @property
    def profile(self):
        return self.definition.profile

    @property
    def metadata(self):
        return self.definition.metadata


class EditorAssetLibrary:
    """
    Independent asset access service for PixelBound Editor.

    Uses Core's AssetCatalog and loads Editor preview images.
    Never imports Game runtime modules.
    """

    def __init__(
        self,
        catalog: AssetCatalog,
        project_root: Path = PROJECT_ROOT,
    ):

        if not isinstance(catalog, AssetCatalog):
            raise TypeError(
                "EditorAssetLibrary requires an AssetCatalog."
            )

        self.catalog = catalog

        self.project_root = Path(
            project_root
        ).resolve()

        self.assets: dict[str, EditorAsset] = {}

        self.missing_assets = []

    # --------------------------------------------------
    # IMAGE LOADING
    # --------------------------------------------------

    def load_preview(self, definition: AssetDefinition):

        if not definition.preview_path:
            return None

        image_path = (
            self.project_root / definition.preview_path
        ).resolve()

        # Prevent paths from escaping the project directory.
        try:
            image_path.relative_to(self.project_root)
        except ValueError:
            raise ValueError(
                f"Asset preview path escapes project root: "
                f"{definition.preview_path}"
            )

        if not image_path.is_file():
            return None

        image = pygame.image.load(str(image_path))

        # Conversion is available after a display mode exists.
        if pygame.display.get_surface() is not None:
            image = image.convert_alpha()

        return image

    # --------------------------------------------------
    # LOAD ALL ASSETS
    # --------------------------------------------------

    def load_assets(self):

        self.assets.clear()
        self.missing_assets.clear()

        for definition in self.catalog.get_all():

            image = self.load_preview(definition)

            if image is None:
                self.missing_assets.append(definition.id)
                continue

            editor_asset = EditorAsset(
                definition=definition,
                image=image,
            )

            self.assets[definition.id] = editor_asset

        if self.missing_assets:
            print(
                "Editor assets without previews:",
                self.missing_assets,
            )

        print(
            "Editor asset count:",
            len(self.assets),
        )

        return self.assets

    # --------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------

    def get(self, asset_id: str):

        return self.assets.get(
            str(asset_id).strip().lower()
        )

    def get_by_category(self, category: str):

        category = str(category).strip().upper()

        return [
            asset
            for asset in self.assets.values()
            if asset.category == category
        ]

    def get_categories(self):

        return sorted({
            asset.category
            for asset in self.assets.values()
        })

    def get_all(self):

        return list(self.assets.values())

    def __len__(self):

        return len(self.assets)
