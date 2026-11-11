
import json
from dataclasses import asdict
from pathlib import Path

from pixelbound_core.assets.asset_catalog import AssetCatalog
from pixelbound_core.assets.asset_definition import AssetDefinition


FORMAT_VERSION = 1


def save_asset_catalog(catalog: AssetCatalog, path):

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "format_version": FORMAT_VERSION,
        "assets": [
            asdict(asset)
            for asset in catalog.get_all()
        ],
    }

    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    temporary_path.replace(path)

    print("Asset catalog saved:", path)
    print("Registered definitions:", len(catalog))


def load_asset_catalog(path) -> AssetCatalog:

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Asset catalog not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Invalid asset catalog format.")

    if data.get("format_version") != FORMAT_VERSION:
        raise ValueError(
            "Unsupported asset catalog format version."
        )

    definitions = data.get("assets")

    if not isinstance(definitions, list):
        raise ValueError(
            "Catalog must contain an assets list."
        )

    catalog = AssetCatalog()

    for index, definition_data in enumerate(definitions):

        if not isinstance(definition_data, dict):
            raise ValueError(
                f"Invalid asset definition at index {index}."
            )

        try:
            definition = AssetDefinition(**definition_data)
            catalog.register(definition)

        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid asset definition at index {index}: {error}"
            ) from error

    return catalog
