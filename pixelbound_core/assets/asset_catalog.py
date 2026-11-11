
from pixelbound_core.assets.asset_definition import AssetDefinition


class AssetCatalog:
    """
    Central registry for PixelBound asset definitions.

    Stores metadata only. Does not load images or create
    Game runtime objects.
    """

    def __init__(self):
        self._assets: dict[str, AssetDefinition] = {}

    # --------------------------------------------------
    # REGISTRATION
    # --------------------------------------------------

    def register(
        self,
        asset_definition: AssetDefinition,
        *,
        replace: bool = False,
    ):
        if not isinstance(asset_definition, AssetDefinition):
            raise TypeError(
                "Expected an AssetDefinition instance."
            )

        asset_id = asset_definition.id

        if asset_id in self._assets and not replace:
            raise ValueError(
                f"Asset already registered: {asset_id}"
            )

        self._assets[asset_id] = asset_definition

    # --------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------

    def get(self, asset_id: str):
        return self._assets.get(str(asset_id).strip().lower())

    def get_by_category(self, category: str):
        category = str(category).strip().upper()

        return [
            asset
            for asset in self._assets.values()
            if asset.category == category
        ]

    def get_categories(self):
        return sorted({
            asset.category
            for asset in self._assets.values()
        })

    def get_all(self):
        return list(self._assets.values())

    # --------------------------------------------------
    # MANAGEMENT
    # --------------------------------------------------

    def unregister(self, asset_id: str):
        return self._assets.pop(
            str(asset_id).strip().lower(),
            None,
        )

    def clear(self):
        self._assets.clear()

    def __len__(self):
        return len(self._assets)

    def __contains__(self, asset_id):
        return str(asset_id).strip().lower() in self._assets
