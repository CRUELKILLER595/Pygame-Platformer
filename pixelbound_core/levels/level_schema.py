
"""Shared PixelBound level data structure."""

LEVEL_FORMAT_VERSION = 1

DEFAULT_TIMER_SECONDS = 120


def create_empty_level(level_name="Untitled"):

    return {
        "version": LEVEL_FORMAT_VERSION,
        "level_name": str(level_name),
        "soundtrack": "",
        "timer_seconds": DEFAULT_TIMER_SECONDS,
        "objects": [],
    }


def normalize_level_data(data, default_name="Untitled"):
    """
    Normalize level metadata while preserving unknown fields
    for backward compatibility and future extensions.
    """

    if not isinstance(data, dict):
        raise ValueError("Level data must be a JSON object.")

    result = dict(data)

    result.setdefault("version", LEVEL_FORMAT_VERSION)

    result.setdefault("level_name", default_name)

    if not isinstance(result["level_name"], str):
        raise ValueError("level_name must be a string.")

    # Migrate the older field name.
    if not result.get("soundtrack"):
        result["soundtrack"] = result.get("soundtracks", "")

    result.pop("soundtracks", None)

    if not isinstance(result["soundtrack"], str):
        raise ValueError("soundtrack must be a string.")

    result.setdefault(
        "timer_seconds",
        DEFAULT_TIMER_SECONDS,
    )

    if isinstance(result["timer_seconds"], bool):
        raise ValueError("timer_seconds must be an integer.")

    try:
        result["timer_seconds"] = int(
            result["timer_seconds"]
        )
    except (TypeError, ValueError):
        raise ValueError("Invalid timer_seconds value.")

    if not 1 <= result["timer_seconds"] <= 3600:
        raise ValueError("Timer must be between 1 and 3600 seconds.")

    result.setdefault("objects", [])

    if not isinstance(result["objects"], list):
        raise ValueError("Level objects must be a list.")

    return result
