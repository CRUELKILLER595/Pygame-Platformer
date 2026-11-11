
from copy import deepcopy
import re


PROFILE_VERSION = 1


# ============================================================
# ASSET ID NORMALIZATION
# ============================================================

def normalize_asset_id(value):
    """Normalize asset IDs, folder names and display names consistently."""

    value = str(value or "").strip().lower()

    # Remove dimensions or other parenthesized suffixes.
    value = re.sub(r"\([^)]*\)", "", value)

    # Convert spaces and punctuation into underscores.
    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")


# ============================================================
# INDIVIDUAL ASSET PROFILES
# ============================================================

ASSET_PROFILES = {

    # --------------------------------------------------------
    # SPIKES
    # --------------------------------------------------------

    "spikes": {
        "aliases": [
            "spike"
        ],
        "category": "TRAPS",
        "visual_size_tiles": (1.0,0.50),
        "anchor": "bottom_center",
        "frame_sizes": {},
        "collision": {
            "type": "hazard",
            "box": (0.03, 0.30, 0.94, 0.66),
        },
        "animation": {
            "default": "on",
            "speed": 4,
        },
    },
    "spike_head": {
    "aliases": [
        "spike-head",
        "spike head",
    ],
    "category": "TRAPS",

    "visual_size_tiles": (1.0, 1.0),
    "anchor": "bottom_center",

    "frame_sizes": {
        "blink": (54, 52),
        "bottom_hit": (54, 52),
        "idle": (54, 52),
        "left_hit": (54, 52),
        "right_hit": (54, 52),
        "top_hit": (54, 52),
    },

    "collision": {
        # Spike Head contact should trigger the hazard handler.
        "type": "hazard",
        "box": (0.03, 0.03, 0.94, 0.94),
    },

    "animation": {
        "default": "idle",
        "speed": 5,
    },
},

    # --------------------------------------------------------
    # FIRE
    # --------------------------------------------------------

    "fire": {
        "aliases": [
            "fire_trap",
            "flame",
            "flames",
        ],
        "category": "TRAPS",
        "visual_size_tiles": (1,3),
        "anchor": "bottom_center",
        "frame_sizes": {
            "on": (16, 32),
            "off": (16, 32),
            "hit": (32, 32),
        },
        "collision": {
            "type": "hazard",
            "box": (0.20, 0.20, 0.60, 0.76),
        },
        "animation": {
            "default": "on",
            "speed": 3,
        },
    },

    # --------------------------------------------------------
    # FAN
    # --------------------------------------------------------

    "fan": {
        "aliases": [
            "fan_trap",
            "propeller",
        ],
        "category": "TRAPS",
        "visual_size_tiles": (1.0, 0.65),
        "anchor": "bottom_center",
        "frame_sizes": {
            "on": (24, 8),
            "off": (24, 8),
        },
        "collision": {
            "type": "hazard",
            "box": (0.10, 0.08, 0.80, 0.82),
        },
        "animation": {
            "default": "on",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # SAW
    # --------------------------------------------------------

    "saw": {
        "aliases": [
            "saw_trap",
            "circular_saw",
            "sawblade",
            "saw_blade",
        ],
        "category": "TRAPS",
        "visual_size_tiles": (0.92, 0.92),
        "anchor": "bottom_center",
        "frame_sizes": {
            "on": (38, 38),
            "off": (38, 38),
        },
        "collision": {
            "type": "hazard",
            "box": (0.15, 0.15, 0.70, 0.70),
        },
        "animation": {
            "default": "on",
            "speed": 3,
        },
    },

    # --------------------------------------------------------
    # FALLING PLATFORMS
    # --------------------------------------------------------

    "falling_platforms": {
        "aliases": [
            "falling_platform",
            "falling_platform_trap",
        ],
        "category": "TRAPS",
        "visual_size_tiles": (1.0, 0.6),
        "anchor": "bottom_center",
        "frame_sizes": {
            "on": (32, 10),
            "off": (32, 10),
        },
        "collision": {
            "type": "platform",
            "box": (0.01, 0.04, 0.98, 0.30),
        },
        "animation": {
            "default": "on",
            "speed": 4,
        },
    },

    # --------------------------------------------------------
    # TRAMPOLINE / SPRING PAD
    # --------------------------------------------------------

    "trampoline": {
        "aliases": [
            "trampoline_trap",
            "jump_pad",
            "spring_pad",
        ],
        "category": "TRAPS",
        "visual_size_tiles": (1.0, 0.65),
        "anchor": "bottom_center",
        "frame_sizes": {},
        "collision": {
            "type": "spring",
            "box": (0.04, 0.05, 0.92, 0.30),
        },
        "animation": {
            "default": "on",
            "speed": 4,
        },
    },
}


# ============================================================
# ENEMY PROFILE HELPER
# ============================================================

def _enemy_profile(size_tiles, collision_box):
    """Create consistent profile fields for a specific enemy."""

    return {
        "category": "ENEMIES",
        "visual_size_tiles": size_tiles,
        "anchor": "bottom_center",
        "frame_sizes": {},
        "collision": {
            "type": "hazard",
            "box": collision_box,
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    }


# ============================================================
# BEE PROFILES
# ============================================================

for enemy_id in (
    "enemy_bee_black",
    "enemy_bee_blue",
):
    ASSET_PROFILES[enemy_id] = _enemy_profile(
        (0.62, 0.62),
        (0.14, 0.14, 0.72, 0.72),
    )


# ============================================================
# FROG PROFILES
# ============================================================

for enemy_id in (
    "enemy_frog_green",
    "enemy_frog_orange",
    "enemy_frog_red",
):
    ASSET_PROFILES[enemy_id] = _enemy_profile(
        (0.80, 0.80),
        (0.10, 0.12, 0.80, 0.82),
    )


# ============================================================
# SHEEP PROFILES
# ============================================================

for enemy_id in (
    "enemy_sheep_blue",
    "enemy_sheep_green",
    "enemy_sheep_red",
    "enemy_sheep_yellow",
):
    ASSET_PROFILES[enemy_id] = _enemy_profile(
        (0.84, 0.84),
        (0.10, 0.14, 0.80, 0.80),
    )


# ============================================================
# TURTLE PROFILES
# ============================================================

for enemy_id in (
    "enemy_turtle_blue",
    "enemy_turtle_green",
    "enemy_turtle_red",
    "enemy_turtle_yellow",
):
    ASSET_PROFILES[enemy_id] = _enemy_profile(
        (1.12, 1.32),
        (0.08, 0.12, 0.84, 0.86),
    )


# ============================================================
# CATEGORY DEFAULTS
# ============================================================

CATEGORY_DEFAULTS = {

    # --------------------------------------------------------
    # TRAPS
    # --------------------------------------------------------

    "TRAPS": {
        # None means use the trimmed source dimensions as a
        # fallback bounded by the loader's sizing rules.
        "visual_size_tiles": None,
        "anchor": "bottom_center",
        "frame_sizes": {},
        "collision": {
            "type": "hazard",
            "box": (0.14, 0.16, 0.72, 0.76),
        },
        "animation": {
            "default": "on",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # BREAKABLES
    # --------------------------------------------------------

    "BREAKABLES": {
        "visual_size_tiles": (1.0, 1.0),
        "anchor": "bottom_center",
        "frame_sizes": {},
        "collision": {
            "type": "solid",
            "box": (0.0, 0.0, 1.0, 1.0),
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # SOLID TILES
    # --------------------------------------------------------

    "TILES": {
        "visual_size_tiles": (1.0, 1.0),
        "anchor": "top_left",
        "frame_sizes": {},
        "collision": {
            "type": "solid",
            "box": (0.0, 0.0, 1.0, 1.0),
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # COLLECTIBLES
    # --------------------------------------------------------

    "COLLECTIBLES": {
        # Keep the original rendering behavior until fruit
        # visuals and collection geometry are migrated together.
        "visual_size_tiles": (1.0, 1.0),
        "anchor": "top_left",
        "frame_sizes": {},
        "collision": {
            "type": "collectible",
            "box": (0.0, 0.0, 1.0, 1.0),
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # ENEMIES
    # --------------------------------------------------------

    "ENEMIES": {
        "visual_size_tiles": None,
        "anchor": "bottom_center",
        "frame_sizes": {},
        "collision": {
            "type": "hazard",
            "box": (0.12, 0.12, 0.76, 0.82),
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # LEVEL OBJECTS
    # --------------------------------------------------------

    "LEVEL": {
        "visual_size_tiles": (1.0, 1.0),
        "anchor": "top_left",
        "frame_sizes": {},
        "collision": {
            "type": "trigger",
            "box": (0.0, 0.0, 1.0, 1.0),
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # BACKGROUNDS
    # --------------------------------------------------------

    "BACKGROUNDS": {
        "visual_size_tiles": None,
        "anchor": "top_left",
        "frame_sizes": {},
        "collision": {
            "type": "none",
            "box": None,
        },
        "animation": {
            "default": "idle",
            "speed": 5,
        },
    },

    # --------------------------------------------------------
    # EFFECTS
    # --------------------------------------------------------

    "EFFECTS": {
        "visual_size_tiles": (1.0, 1.0),
        "anchor": "center",
        "frame_sizes": {},
        "collision": {
            "type": "none",
            "box": None,
        },
        "animation": {
            "default": "idle",
            "speed": 4,
        },
    },
}


# ============================================================
# PROFILE LOOKUP
# ============================================================

def get_asset_profile(asset_id=None, category=None, name=None):
    """
    Return an independent profile for the most specific asset.

    Lookup order:
      1. Exact normalized ID or name.
      2. Exact alias.
      3. Recognized profile name contained in the ID or name.
      4. Category default.
    """

    candidates = [
        normalize_asset_id(asset_id),
        normalize_asset_id(name),
    ]

    candidates = [
        candidate
        for candidate in candidates
        if candidate
    ]

    category_key = str(category or "").strip().upper()

    # --------------------------------------------------------
    # EXACT ID / NAME / ALIAS MATCH
    # --------------------------------------------------------

    for key, profile in ASSET_PROFILES.items():

        if (
            category_key
            and profile.get("category") != category_key
        ):
            continue

        aliases = {
            normalize_asset_id(alias)
            for alias in profile.get("aliases", [])
        }

        if any(
            candidate == key or candidate in aliases
            for candidate in candidates
        ):
            return deepcopy(profile)

    # --------------------------------------------------------
    # PARTIAL MATCH
    # --------------------------------------------------------

    for key, profile in ASSET_PROFILES.items():

        if (
            category_key
            and profile.get("category") != category_key
        ):
            continue

        possible_names = [
            key,
            *profile.get("aliases", []),
        ]

        for possible_name in possible_names:

            normalized_name = normalize_asset_id(
                possible_name
            )

            if not normalized_name:
                continue

            if any(
                normalized_name in candidate
                for candidate in candidates
            ):
                return deepcopy(profile)

    # --------------------------------------------------------
    # CATEGORY FALLBACK
    # --------------------------------------------------------

    profile = deepcopy(
        CATEGORY_DEFAULTS.get(category_key, {})
    )

    profile.setdefault("visual_size_tiles", None)
    profile.setdefault("anchor", "top_left")
    profile.setdefault("frame_sizes", {})

    profile.setdefault(
        "collision",
        {
            "type": "none",
            "box": None,
        },
    )

    profile.setdefault(
        "animation",
        {
            "default": None,
            "speed": 5,
        },
    )

    profile["category"] = category_key or None

    return profile


# ============================================================
# VISUAL DIMENSION CALCULATION
# ============================================================

def visual_size_pixels(
    profile,
    tile_size,
    fallback_size=None,
):
    """
    Convert visual_size_tiles into pixel dimensions.

    These dimensions describe the maximum visual canvas.
    Sprite aspect ratio should be preserved by the loader.
    """

    size_tiles = (profile or {}).get(
        "visual_size_tiles"
    )

    if size_tiles is None:

        if fallback_size is not None:
            return tuple(
                max(1, int(value))
                for value in fallback_size
            )

        return int(tile_size), int(tile_size)

    width_tiles, height_tiles = size_tiles

    return (
        max(
            1,
            round(float(width_tiles) * tile_size),
        ),
        max(
            1,
            round(float(height_tiles) * tile_size),
        ),
    )


# ============================================================
# GRID ANCHOR PLACEMENT
# ============================================================

def place_rect_in_cell(
    rect,
    cell_x,
    cell_y,
    tile_size,
    anchor="top_left",
):
    """Position a rectangle consistently relative to its grid cell."""

    cell_x = int(cell_x)
    cell_y = int(cell_y)
    tile_size = int(tile_size)

    if anchor == "bottom_center":

        rect.midbottom = (
            cell_x + tile_size // 2,
            cell_y + tile_size,
        )

    elif anchor == "bottom_left":

        rect.bottomleft = (
            cell_x,
            cell_y + tile_size,
        )

    elif anchor == "center":

        rect.center = (
            cell_x + tile_size // 2,
            cell_y + tile_size // 2,
        )

    elif anchor == "top_center":

        rect.midtop = (
            cell_x + tile_size // 2,
            cell_y,
        )

    elif anchor == "top_right":

        rect.topright = (
            cell_x + tile_size,
            cell_y,
        )

    elif anchor == "bottom_right":

        rect.bottomright = (
            cell_x + tile_size,
            cell_y + tile_size,
        )

    else:
        # Default: top-left / grid-cell origin.
        rect.topleft = (
            cell_x,
            cell_y,
        )

    return rect
