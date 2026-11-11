"""Compatibility helpers backed by the unified asset profile registry."""

from pixelbound_core.assets.asset_profiles import (
    ASSET_PROFILES,
    CATEGORY_DEFAULTS,
    normalize_asset_id,
)


DEBUG_HITBOXES = False

DEFAULT_TRAP_HITBOX = CATEGORY_DEFAULTS["TRAPS"]["collision"]["box"]
DEFAULT_ENEMY_HITBOX = CATEGORY_DEFAULTS["ENEMIES"]["collision"]["box"]

# Keep the old public constant available to existing code, but derive it from
# asset_profiles.py so trap collision geometry has only one source of truth.
TRAP_HITBOX_PROFILES = {}
for _asset_id, _profile in ASSET_PROFILES.items():
    if _profile.get("category") != "TRAPS":
        continue
    _collision_box = _profile.get("collision", {}).get("box")
    if not _collision_box:
        continue
    TRAP_HITBOX_PROFILES[_asset_id] = _collision_box
    for _alias in _profile.get("aliases", []):
        TRAP_HITBOX_PROFILES[normalize_asset_id(_alias)] = _collision_box

# Enemy profiles remain here until the enemy registry is migrated to the
# unified profile system. Explicit per-enemy geometry is preserved.
ENEMY_HITBOX_PROFILES = {
    "slime": (0.10, 0.28, 0.80, 0.68),
    "bat": (0.16, 0.16, 0.68, 0.68),
    "spider": (0.12, 0.18, 0.76, 0.76),
    "beetle": (0.10, 0.22, 0.80, 0.72),
    "ghost": (0.15, 0.12, 0.70, 0.80),
    "goblin": (0.18, 0.12, 0.64, 0.84),
}


def normalize_asset_name(name):
    return normalize_asset_id(name)


def profile_for(name, profiles, default):
    key = normalize_asset_name(name)
    if key in profiles:
        return profiles[key]

    # Also support display names such as "Circular Saw Trap".
    for profile_name, profile in profiles.items():
        if profile_name in key:
            return profile
    return default


def make_collision_rect(sprite_rect, ratios):
    """Build a collision rectangle from normalized (x, y, width, height)."""
    rx, ry, rw, rh = ratios
    left = sprite_rect.left + round(sprite_rect.width * rx)
    top = sprite_rect.top + round(sprite_rect.height * ry)
    width = max(1, round(sprite_rect.width * rw))
    height = max(1, round(sprite_rect.height * rh))
    return sprite_rect.__class__(left, top, width, height)
