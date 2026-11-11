
"""Validation utilities for PixelBound level documents."""

from pixelbound_core.levels.level_schema import (
    normalize_level_data,
)


def validate_level_data(data, known_asset_ids=None):
    """
    Return a list of validation errors.

    known_asset_ids is optional. When supplied, object IDs
    are checked against the shared asset catalog.
    """

    errors = []

    try:
        document = normalize_level_data(data)

    except ValueError as error:
        return [str(error)]

    for index, obj in enumerate(document["objects"]):

        prefix = f"Object {index}"

        if not isinstance(obj, dict):
            errors.append(
                f"{prefix} must be a JSON object."
            )
            continue

        asset_id = obj.get("id")

        if not isinstance(asset_id, str) or not asset_id.strip():
            errors.append(
                f"{prefix} has an invalid asset ID."
            )
            continue

        for coordinate in ("x", "y"):

            value = obj.get(coordinate)

            if isinstance(value, bool):
                errors.append(
                    f"{prefix}: {coordinate} must be an integer."
                )
                continue

            try:
                int(value)
            except (TypeError, ValueError):
                errors.append(
                    f"{prefix}: invalid {coordinate} coordinate."
                )

        if known_asset_ids is not None:
            if asset_id not in known_asset_ids:
                errors.append(
                    f"{prefix}: unknown asset ID '{asset_id}'."
                )

    return errors
