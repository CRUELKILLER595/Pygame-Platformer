
"""Serialize and save PixelBound level documents."""

import json
from pathlib import Path

from pixelbound_core.levels.level_schema import (
    normalize_level_data,
)

from pixelbound_core.levels.level_validator import (
    validate_level_data,
)


def save_level_data(level_path, level_data):

    level_path = Path(level_path)

    document = normalize_level_data(
        level_data,
        default_name=level_path.stem,
    )

    errors = validate_level_data(document)

    if errors:
        raise ValueError(
            "Cannot save invalid level:\n"
            + "\n".join(errors)
        )

    level_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = level_path.with_suffix(
        level_path.suffix + ".tmp"
    )

    try:

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                document,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_path.replace(level_path)

    except Exception:

        temporary_path.unlink(missing_ok=True)
        raise

    return level_path
