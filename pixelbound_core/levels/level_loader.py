
"""Load PixelBound level documents."""

import json
from pathlib import Path

from pixelbound_core.levels.level_schema import (
    normalize_level_data,
)
from pixelbound_core.levels.level_schema import (
    create_empty_level,
    normalize_level_data,
)

def load_level_data(path):
    source = Path(path)

    raw = source.read_text(encoding="utf-8-sig")

    # Empty files represent levels that have not been created yet.
    if not raw.strip():
        return create_empty_level(source.stem)

    data = json.loads(raw)

    return normalize_level_data(
        data,
        default_name=source.stem
    )