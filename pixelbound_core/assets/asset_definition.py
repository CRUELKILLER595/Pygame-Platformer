
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetDefinition:
    """
    Application-independent description of a PixelBound asset.

    Contains metadata only. It does not contain Pygame surfaces
    or references to Game runtime classes.
    """

    id: str
    name: str
    category: str

    width: int
    height: int

    # Relative path to an image used by the Editor for preview.
    preview_path: str | None = None

    # Semantic identification, independent of Game classes.
    # Examples: player_spawn, enemy, collectible, terrain.
    role: str | None = None

    score_value: int = 0

    # Shared visual and collision metadata.
    profile: dict[str, Any] = field(
        default_factory=dict
    )

    # Animation descriptions, not loaded Pygame surfaces.
    animation_specs: dict[str, Any] = field(
        default_factory=dict
    )

    # Additional application-independent metadata.
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        self.id = str(self.id).strip().lower()
        self.name = str(self.name).strip()
        self.category = str(self.category).strip().upper()

        if not self.id:
            raise ValueError("Asset ID cannot be empty.")

        if not self.name:
            raise ValueError("Asset name cannot be empty.")

        if not self.category:
            raise ValueError("Asset category cannot be empty.")

        self.width = int(self.width)
        self.height = int(self.height)

        if self.width <= 0 or self.height <= 0:
            raise ValueError(
                "Asset dimensions must be positive."
            )
