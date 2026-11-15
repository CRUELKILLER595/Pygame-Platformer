"""Stable identity helpers for PixelBound levels."""

from uuid import uuid4


def generate_level_id(prefix="custom"):
    """
    Generate a unique, filesystem-safe level ID.

    Example:
        custom_a81f29c4d8e1
    """

    prefix = str(prefix).strip().lower()

    if not prefix or not prefix.replace("_", "").isalnum():
        raise ValueError(
            "Level ID prefix must contain only letters, numbers and underscores."
        )

    return f"{prefix}_{uuid4().hex[:12]}"