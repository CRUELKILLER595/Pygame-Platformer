
import os
import re
import pygame as p

from .animation_loader import load_animation_sheet
from pixelbound_core.assets.asset_profiles import (
    get_asset_profile,
    visual_size_pixels,
)
from pixelbound_core.assets.tile_loader import (
    load_tiles,
    load_character_tile,
)
from game.settings import TILE_SIZE,SPRITE_SIZE

from .enemy_registry import ENEMY_REGISTRY

from game.objects.player import Player
from game.objects.Block import Block
from game.objects.fire import Fire
from game.objects.checkpoint import Checkpoint
from game.objects.start import Start
from game.objects.end import End
from game.objects.fruit import Fruit
from game.objects.boxes import Box
from game.objects.trap import Trap
from game.objects.enemy import Enemy


# ============================================================
# ASSET DIRECTORIES
# ============================================================

ASSET_ROOT = "assets"

TERRAIN = os.path.join(
    ASSET_ROOT,
    "Terrain",
    "Terrain.png",
)

CHARACTERS = os.path.join(
    ASSET_ROOT,
    "MainCharacters",
)

ENEMIES = os.path.join(
    ASSET_ROOT,
    "Enemies",
)

TRAPS = os.path.join(
    ASSET_ROOT,
    "Traps",
)

ITEMS = os.path.join(
    ASSET_ROOT,
    "Items",
)

OTHER = os.path.join(
    ASSET_ROOT,
    "Other",
)

BACKGROUND = os.path.join(
    ASSET_ROOT,
    "Background",
)


FRUIT_SCORES = {
    "Apple": 100,
    "Bananas": 125,
    "Cherries": 150,
    "Kiwi": 175,
    "Melon": 200,
    "Orange": 125,
    "Pineapple": 250,
    "Strawberry": 150,
}


# ============================================================
# ASSET
# ============================================================

class Asset:

    def __init__(
        self,
        id,
        name,
        image,
        category,
        object_class,
        width,
        height,
        animations=None,
        score_value=0,
        profile=None,
    ):

        self.id = id
        self.name = name
        self.image = image

        self.category = category

        self.width = int(width)
        self.height = int(height)

        self.object_class = object_class

        self.animations = animations or {}

        # The editor and runtime use the same asset profile.
        self.profile = (
            profile
            if profile is not None
            else get_asset_profile(
                self.id,
                self.category,
                self.name,
            )
        )

        self.score_value = score_value

        # Used by editor palette hit detection.
       


# ============================================================
# ASSET MANAGER
# ============================================================

class AssetManager:

    def __init__(self):
        self.assets = {}

    # --------------------------------------------------------
    # ASSET REGISTRY
    # --------------------------------------------------------

    def register_asset(self, asset):
        self.assets[asset.id] = asset

    def get(self, asset_id):
        return self.assets.get(asset_id)

    def get_by_category(self, category):
        return [
            asset
            for asset in self.assets.values()
            if asset.category == category
        ]

    def get_categories(self):
        return sorted({
            asset.category
            for asset in self.assets.values()
        })

    # --------------------------------------------------------
    # GENERAL UTILITIES
    # --------------------------------------------------------

    @staticmethod
    def load_image(path):
        return p.image.load(path).convert_alpha()

    @staticmethod
    def make_id(name):
        name = str(name).lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        return name.strip("_")

    @staticmethod
    def parse_frame_size(filename):
        """Read dimensions such as 16x32 from a filename."""

        match = re.search(
            r"(\d+)\s*x\s*(\d+)",
            filename.lower(),
        )

        if match:
            return (
                int(match.group(1)),
                int(match.group(2)),
            )

        return None

    # ========================================================
    # TERRAIN
    # ========================================================

    def load_blocks(self):

        image = self.load_image(TERRAIN)
        tiles = load_tiles(
    image,
    tile_size=TILE_SIZE,
    sprite_size=SPRITE_SIZE,
)

        for tile, row, col in tiles:

            asset = Asset(
                id=f"terrain_{row}_{col}",
                name=f"Terrain {row},{col}",
                image=tile,
                category="TILES",
                object_class=Block,
                width=TILE_SIZE,
                height=TILE_SIZE,
            )

            self.register_asset(asset)

    # ========================================================
    # CHARACTERS
    # ========================================================

    def load_characters(self):

        if not os.path.exists(CHARACTERS):
            return

        for character in os.listdir(CHARACTERS):

            folder = os.path.join(
                CHARACTERS,
                character,
            )

            if not os.path.isdir(folder):
                continue

            idle_path = os.path.join(
                folder,
                "idle.png",
            )

            if not os.path.exists(idle_path):
                continue

            image = self.load_image(idle_path)
            image = load_character_tile(
    image,
    tile_size=TILE_SIZE,
)

            asset = Asset(
                id=self.make_id(character),
                name=character,
                image=image,
                category="CHARACTERS",
                object_class=Player,
                width=TILE_SIZE,
                height=TILE_SIZE,
            )

            self.register_asset(asset)

    # ========================================================
    # TRAP HELPERS
    # ========================================================

    @staticmethod
    def _normalise_trap_animation_name(filename):
   
     stem = os.path.splitext(os.path.basename(filename))[0]

    # Remove sheet dimensions, e.g. (54x52).
     stem = re.sub(
        r"\s*\(\s*\d+\s*x\s*\d+\s*\)\s*$",
        "",
        stem,
        flags=re.IGNORECASE,
    )

    # Remove numeric suffixes, e.g. Idle(3) -> Idle.
     stem = re.sub(
        r"\s*\(\s*\d+\s*\)\s*$",
        "",
        stem,
    )

     return AssetManager.make_id(stem)

    def get_trap_frame_size(
        self,
        trap_name,
        animation_name,
        profile=None,
    ):
        """Resolve a sheet's cell size from its profile or filename."""

        profile = profile or get_asset_profile(
            self.make_id(trap_name),
            "TRAPS",
            trap_name,
        )

        animation_key = self._normalise_trap_animation_name(
            animation_name
        )

        configured_sizes = profile.get(
            "frame_sizes",
            {},
        )

        for configured_state, size in configured_sizes.items():

            if self.make_id(configured_state) == animation_key:
                return tuple(size)

        return self.parse_frame_size(animation_name)

    def get_trap_preview_file(self, files):
        """Choose the most appropriate image for the editor preview."""

        preferred = (
            "on",
            "idle",
            "active",
            "default",
            "walk",
            "off",
        )

        keyed = {
            self._normalise_trap_animation_name(filename): filename
            for filename in files
        }

        for key in preferred:
            if key in keyed:
                return keyed[key]

        return next(
            (
                filename
                for filename in sorted(files)
                if filename.lower().endswith(".png")
            ),
            None,
        )

    # --------------------------------------------------------
    # TRAP FRAME PROCESSING
    # --------------------------------------------------------

    @staticmethod
    def _trim_trap_frames(frames):
        """Trim transparent borders using a shared animation crop."""

        frames = [
            frame
            for frame in (frames or [])
            if isinstance(frame, p.Surface)
        ]

        if not frames:
            return []

        source_size = frames[0].get_size()

        if any(
            frame.get_size() != source_size
            for frame in frames
        ):
            return frames

        bounds = []

        for frame in frames:

            rect = frame.get_bounding_rect(min_alpha=1)

            if rect.width > 0 and rect.height > 0:
                bounds.append(rect)

        if not bounds:
            return frames

        crop = bounds[0].copy()

        for rect in bounds[1:]:
            crop = crop.union(rect)

        crop = crop.clip(
            p.Rect((0, 0), source_size)
        )

        if crop.width <= 0 or crop.height <= 0:
            return frames

        return [
            frame.subsurface(crop).copy()
            for frame in frames
        ]

    @staticmethod
    def _fit_trap_frames(frames, target_size):
        """Fit frames proportionally within a shared visual canvas."""

        target_w, target_h = target_size
        result = []

        for frame in frames:

            source_w, source_h = frame.get_size()

            if source_w <= 0 or source_h <= 0:
                continue

            scale = min(
                target_w / source_w,
                target_h / source_h,
            )

            width = max(
                1,
                min(target_w, round(source_w * scale)),
            )

            height = max(
                1,
                min(target_h, round(source_h * scale)),
            )

            scaled = p.transform.scale(
                frame,
                (width, height),
            )

            canvas = p.Surface(
                (target_w, target_h),
                p.SRCALPHA,
            )

            # Bottom-center alignment keeps the visible art stable.
            canvas.blit(
                scaled,
                (
                    (target_w - width) // 2,
                    target_h - height,
                ),
            )

            result.append(canvas)

        return result

    # ========================================================
    # TRAPS
    # ========================================================

    def load_traps(self):
        """Load traps using their individual visual and collision profiles."""

        if not os.path.isdir(TRAPS):
            print("Trap directory not found:", TRAPS)
            return

        for trap_name in sorted(os.listdir(TRAPS), key=str.lower):

            trap_path = os.path.join(
                TRAPS,
                trap_name,
            )

            if not os.path.isdir(trap_path):
                continue

            asset_id = self.make_id(trap_name)

            profile = get_asset_profile(
                asset_id,
                "TRAPS",
                trap_name,
            )

            png_files = sorted(
                filename
                for filename in os.listdir(trap_path)
                if filename.lower().endswith(".png")
            )

            if not png_files:
                continue

            source_animations = {}

            for filename in png_files:

                image_path = os.path.join(
                    trap_path,
                    filename,
                )

                animation_key = (
                    self._normalise_trap_animation_name(filename)
                )

                source_image = self.load_image(image_path)

                frame_size = self.get_trap_frame_size(
                    trap_name,
                    filename,
                    profile,
                )

                if frame_size:

                    frame_w, frame_h = frame_size

                    if (
                        source_image.get_width() >= frame_w
                        and source_image.get_height() >= frame_h
                    ):

                        frames = load_animation_sheet(
                            image_path,
                            frame_w,
                            frame_h,
                        )

                    else:

                        print(
                            "WARNING: Invalid trap frame size; "
                            "keeping sprite static:",
                            image_path,
                            "image=",
                            source_image.get_size(),
                            "frame=",
                            frame_size,
                        )

                        frames = [source_image]

                else:

                    # No frame dimensions means a static sprite.
                    frames = [source_image]

                    if (
                        source_image.get_width()
                        > source_image.get_height() * 2
                    ):

                        print(
                            "PROFILE NEEDED: possible animated trap sheet:",
                            image_path,
                            "Add its cell dimensions to asset_profiles.py.",
                        )

                frames = [
                    frame
                    for frame in (frames or [])
                    if isinstance(frame, p.Surface)
                ]

                if frames:
                    source_animations[animation_key] = frames

            if not source_animations:
                print("WARNING: No trap frames loaded from:", trap_path)
                continue

            preview_file = self.get_trap_preview_file(png_files)

            preview_key = (
                self._normalise_trap_animation_name(preview_file)
                if preview_file
                else next(iter(source_animations))
            )

            if preview_key not in source_animations:
                preview_key = next(iter(source_animations))

            trimmed_animations = {
                key: self._trim_trap_frames(frames)
                for key, frames in source_animations.items()
            }

            trimmed_animations = {
                key: frames
                for key, frames in trimmed_animations.items()
                if frames
            }

            if not trimmed_animations:
                print("WARNING: No usable trap art:", trap_name)
                continue

            if preview_key not in trimmed_animations:
                preview_key = next(iter(trimmed_animations))

            configured_size = profile.get("visual_size_tiles")

            if configured_size is not None:

                display_size = visual_size_pixels(
                    profile,
                    TILE_SIZE,
                )

            else:

                base_w, base_h = (
                    trimmed_animations[preview_key][0].get_size()
                )

                scale = TILE_SIZE / max(base_w, base_h, 1)

                display_size = (
                    max(1, round(base_w * scale)),
                    max(1, round(base_h * scale)),
                )

            display_animations = {
                key: self._fit_trap_frames(frames, display_size)
                for key, frames in trimmed_animations.items()
            }

            display_animations = {
                key: frames
                for key, frames in display_animations.items()
                if frames
            }

            if not display_animations:
                print("WARNING: No usable trap animations:", trap_name)
                continue

            if preview_key not in display_animations:
                preview_key = next(iter(display_animations))

            preview = display_animations[preview_key][0]

            asset = Asset(
                id=asset_id,
                name=trap_name,
                image=preview,
                category="TRAPS",
                object_class=Trap,
                width=display_size[0],
                height=display_size[1],
                animations=display_animations,
                profile=profile,
            )

            asset.preview_animation = preview_key

            # Registration ensures TRAPS appears in editor categories.
            self.register_asset(asset)

            print(
                "TRAP PROFILE:",
                trap_name,
                "visual=",
                display_size,
                "anchor=",
                profile.get("anchor"),
                "collision=",
                profile.get("collision"),
                "animations=",
                {
                    key: len(frames)
                    for key, frames in display_animations.items()
                },
            )

    # ========================================================
    # FRUITS / COLLECTIBLES
    # ========================================================

    def load_fruits(self):

        path = os.path.join(
            ITEMS,
            "Fruits",
        )

        if not os.path.exists(path):
            return

        collected_path = os.path.join(
            path,
            "Collected.png",
        )

        collected_frames = []

        if os.path.exists(collected_path):

            collected_frames = load_animation_sheet(
                collected_path,
                32,
                32,
            )

        for filename in os.listdir(path):

            if not filename.lower().endswith(".png"):
                continue

            if filename.lower() == "collected.png":
                continue

            fruit_name = os.path.splitext(filename)[0]

            image_path = os.path.join(
                path,
                filename,
            )

            frames = load_animation_sheet(
                image_path,
                32,
                32,
            )

            if not frames:
                print("WARNING: No fruit frames loaded:", image_path)
                continue

            score = FRUIT_SCORES.get(
                fruit_name,
                100,
            )

            asset = Asset(
                id=self.make_id(fruit_name),
                name=fruit_name,
                image=frames[0],
                category="COLLECTIBLES",
                object_class=Fruit,
                width=TILE_SIZE,
                height=TILE_SIZE,
                animations={
                    "idle": frames,
                    "collected": collected_frames,
                },
                score_value=score,
            )

            self.register_asset(asset)

    # --------------------------------------------------------
    # COLLECTION EFFECT
    # --------------------------------------------------------

    def load_collection_effect(self):

        path = os.path.join(
            ITEMS,
            "Fruits",
            "Collected.png",
        )

        if not os.path.exists(path):
            return

        frames = load_animation_sheet(
            path,
            32,
            32,
        )

        if not frames:
            return

        asset = Asset(
            id="collected_effect",
            name="Collected",
            image=frames[0],
            category="EFFECTS",
            object_class=None,
            width=TILE_SIZE,
            height=TILE_SIZE,
            animations={
                "collected": frames,
            },
        )

        self.register_asset(asset)

    # ========================================================
    # BREAKABLE BOXES
    # ========================================================

    def load_boxes(self):
        """Load breakables using the shared asset-profile system."""

        path = os.path.join(
            ITEMS,
            "Boxes",
        )

        if not os.path.isdir(path):
            return

        for box_name in sorted(os.listdir(path), key=str.lower):

            box_path = os.path.join(
                path,
                box_name,
            )

            if not os.path.isdir(box_path):
                continue

            asset_id = self.make_id(box_name)

            profile = get_asset_profile(
                asset_id,
                "BREAKABLES",
                box_name,
            )

            png_files = sorted(
                filename
                for filename in os.listdir(box_path)
                if filename.lower().endswith(".png")
            )

            if not png_files:
                continue

            source_animations = {}

            for filename in png_files:

                image_path = os.path.join(
                    box_path,
                    filename,
                )

                animation_key = (
                    self._normalise_trap_animation_name(filename)
                )

                source_image = self.load_image(image_path)

                frame_size = self.get_trap_frame_size(
                    box_name,
                    filename,
                    profile,
                )

                if frame_size:

                    frame_w, frame_h = frame_size

                    if (
                        source_image.get_width() >= frame_w
                        and source_image.get_height() >= frame_h
                    ):

                        frames = load_animation_sheet(
                            image_path,
                            frame_w,
                            frame_h,
                        )

                    else:

                        print(
                            "WARNING: Invalid box frame size:",
                            image_path,
                            frame_size,
                        )

                        frames = [source_image]

                else:
                    frames = [source_image]

                frames = [
                    frame
                    for frame in (frames or [])
                    if isinstance(frame, p.Surface)
                ]

                if frames:
                    source_animations[animation_key] = frames

            if not source_animations:
                print("WARNING: No breakable frames loaded from:", box_path)
                continue

            default_animation = profile.get(
                "animation", {}
            ).get("default", "idle")

            if default_animation in source_animations:
                preview_key = default_animation

            elif "idle" in source_animations:
                preview_key = "idle"

            else:
                preview_key = next(iter(source_animations))

            trimmed_animations = {
                key: self._trim_trap_frames(frames)
                for key, frames in source_animations.items()
            }

            trimmed_animations = {
                key: frames
                for key, frames in trimmed_animations.items()
                if frames
            }

            if not trimmed_animations:
                continue

            if preview_key not in trimmed_animations:
                preview_key = next(iter(trimmed_animations))

            display_size = visual_size_pixels(
                profile,
                TILE_SIZE,
                fallback_size=(TILE_SIZE, TILE_SIZE),
            )

            display_animations = {
                key: self._fit_trap_frames(frames, display_size)
                for key, frames in trimmed_animations.items()
            }

            display_animations = {
                key: frames
                for key, frames in display_animations.items()
                if frames
            }

            if not display_animations:
                continue

            if preview_key not in display_animations:
                preview_key = next(iter(display_animations))

            asset = Asset(
                id=asset_id,
                name=box_name,
                image=display_animations[preview_key][0],
                category="BREAKABLES",
                object_class=Box,
                width=display_size[0],
                height=display_size[1],
                animations=display_animations,
                profile=profile,
            )

            asset.preview_animation = preview_key

            self.register_asset(asset)

            print(
                "BREAKABLE PROFILE:",
                box_name,
                "visual=",
                display_size,
                "anchor=",
                profile.get("anchor"),
            )

    # ========================================================
    # CHECKPOINT
    # ========================================================

    def load_checkpoint(self):

        path = os.path.join(
            ITEMS,
            "Checkpoints",
            "Checkpoint",
            "Checkpoint (No Flag).png",
        )

        if not os.path.exists(path):
            return

        image = self.load_image(path)

        image = p.transform.scale(
            image,
            (TILE_SIZE, TILE_SIZE),
        )

        asset = Asset(
            id="checkpoint",
            name="Checkpoint",
            image=image,
            category="LEVEL",
            object_class=Checkpoint,
            width=TILE_SIZE,
            height=TILE_SIZE,
        )

        self.register_asset(asset)

    # ========================================================
    # START
    # ========================================================

    def load_start(self):

        path = os.path.join(
            ITEMS,
            "Checkpoints",
            "Start",
            "Start (Idle)(1).png",
        )

        if not os.path.exists(path):
            return

        image = self.load_image(path)

        image = p.transform.scale(
            image,
            (TILE_SIZE, TILE_SIZE),
        )

        asset = Asset(
            id="start",
            name="Start",
            image=image,
            category="LEVEL",
            object_class=Start,
            width=TILE_SIZE,
            height=TILE_SIZE,
        )

        self.register_asset(asset)

    # ========================================================
    # ENEMY SPRITE SHEET LOADER
    # ========================================================

    def load_enemy_frames(
        self,
        image_path,
        frame_width,
        frame_height,
    ):
        """Extract source frames without resizing them yet."""

        if frame_width <= 0 or frame_height <= 0:
            raise ValueError(
                "Enemy frame dimensions must be positive."
            )

        sheet = self.load_image(image_path)

        sheet_width, sheet_height = sheet.get_size()

        frames = []

        for y in range(
            0,
            sheet_height - frame_height + 1,
            frame_height,
        ):

            for x in range(
                0,
                sheet_width - frame_width + 1,
                frame_width,
            ):

                frame = sheet.subsurface(
                    p.Rect(
                        x,
                        y,
                        frame_width,
                        frame_height,
                    )
                ).copy()

                frames.append(frame)

        if not frames:
            print(
                "WARNING: No complete enemy frames found:",
                image_path,
            )

        return frames

    # --------------------------------------------------------
    # ENEMY TRANSPARENCY TRIMMING
    # --------------------------------------------------------

    @staticmethod
    def _trim_enemy_animation_frames(animations):
        """Trim transparent padding with a stable crop per animation."""

        trimmed_animations = {}

        for animation_name, frames in animations.items():

            frames = [
                frame
                for frame in (frames or [])
                if isinstance(frame, p.Surface)
            ]

            if not frames:
                continue

            frame_size = frames[0].get_size()

            if any(
                frame.get_size() != frame_size
                for frame in frames
            ):

                print(
                    "WARNING: Mixed frame dimensions in enemy animation:",
                    animation_name,
                )

                trimmed_animations[animation_name] = frames
                continue

            bounds = [
                frame.get_bounding_rect(min_alpha=1)
                for frame in frames
            ]

            bounds = [
                rect
                for rect in bounds
                if rect.width > 0 and rect.height > 0
            ]

            if not bounds:
                trimmed_animations[animation_name] = frames
                continue

            # One common crop for all frames in this animation.
            crop = bounds[0].copy()

            for rect in bounds[1:]:
                crop.union_ip(rect)

            crop = crop.clip(
                p.Rect(0, 0, *frame_size)
            )

            if crop.width <= 0 or crop.height <= 0:
                trimmed_animations[animation_name] = frames
                continue

            trimmed_animations[animation_name] = [
                frame.subsurface(crop).copy()
                for frame in frames
            ]

        return trimmed_animations

    # --------------------------------------------------------
    # ENEMY FRAME SIZING
    # --------------------------------------------------------

    @staticmethod
    def _fit_enemy_animations(animations, target_size):
        """
        Preserve aspect ratio and fit all frames on a common canvas.

        Each animation frame uses the same dimensions so switching
        animation states does not unexpectedly resize the enemy.
        """

        target_w = int(target_size[0])
        target_h = int(target_size[1])

        if target_w <= 0 or target_h <= 0:
            raise ValueError(
                "Enemy target dimensions must be positive."
            )

        fitted_animations = {}

        for animation_name, frames in animations.items():

            fitted_frames = []

            for frame in frames:

                source_w, source_h = frame.get_size()

                if source_w <= 0 or source_h <= 0:
                    continue

                scale = min(
                    target_w / source_w,
                    target_h / source_h,
                )

                width = max(
                    1,
                    min(target_w, round(source_w * scale)),
                )

                height = max(
                    1,
                    min(target_h, round(source_h * scale)),
                )

                scaled = p.transform.scale(
                    frame,
                    (width, height),
                )

                canvas = p.Surface(
                    (target_w, target_h),
                    p.SRCALPHA,
                )

                # Center horizontally and align the visible sprite
                # to the bottom of its canvas.
                canvas.blit(
                    scaled,
                    (
                        (target_w - width) // 2,
                        target_h - height,
                    ),
                )

                fitted_frames.append(canvas)

            if fitted_frames:
                fitted_animations[animation_name] = fitted_frames

        return fitted_animations

    # ========================================================
    # ENEMIES
    # ========================================================

    def load_enemies(self):
        """Load enemies from the registry and apply individual profiles."""

        if not os.path.isdir(ENEMIES):
            print("Enemy directory not found:", ENEMIES)
            return

        for enemy_id, definition in ENEMY_REGISTRY.items():

            enemy_name = definition.get(
                "name",
                enemy_id,
            )

            animations = {}

            # -----------------------------------------------
            # LOAD SOURCE ANIMATIONS
            # -----------------------------------------------

            for animation_name, sheet_info in definition.get(
                "animations", {}
            ).items():

                filename = sheet_info.get("file")
                frame_size = sheet_info.get("frame_size")

                if (
                    not filename
                    or not frame_size
                    or len(frame_size) != 2
                ):

                    print(
                        "WARNING: Invalid enemy animation definition:",
                        enemy_id,
                        animation_name,
                    )

                    continue

                image_path = os.path.join(
                    ENEMIES,
                    filename,
                )

                if not os.path.isfile(image_path):

                    print(
                        "WARNING: Enemy animation file not found:",
                        image_path,
                    )

                    continue

                try:

                    frames = self.load_enemy_frames(
                        image_path,
                        int(frame_size[0]),
                        int(frame_size[1]),
                    )

                except (OSError, ValueError, p.error) as error:

                    print(
                        "WARNING: Could not load enemy animation:",
                        image_path,
                        error,
                    )

                    continue

                if frames:
                    animations[str(animation_name).lower()] = frames

            if not animations:

                print(
                    "WARNING: No usable enemy animations:",
                    enemy_id,
                )

                continue

            # -----------------------------------------------
            # TRIM TRANSPARENT BORDERS
            # -----------------------------------------------

            animations = self._trim_enemy_animation_frames(
                animations
            )

            if not animations:

                print(
                    "WARNING: No trimmed enemy animations:",
                    enemy_id,
                )

                continue

            # -----------------------------------------------
            # RESOLVE ASSET PROFILE
            # -----------------------------------------------

            profile = get_asset_profile(
                enemy_id,
                "ENEMIES",
                enemy_name,
            )

            preview_frames = (
                animations.get("idle")
                or next(iter(animations.values()), [])
            )

            if not preview_frames:
                continue

            # -----------------------------------------------
            # CALCULATE TARGET CANVAS
            # -----------------------------------------------

            if profile.get("visual_size_tiles") is None:

                # Generic fallback: fit the largest dimension
                # within one tile and preserve aspect ratio.
                source_w, source_h = preview_frames[0].get_size()

                scale = min(
                    TILE_SIZE / max(1, source_w),
                    TILE_SIZE / max(1, source_h),
                )

                target_size = (
                    max(1, round(source_w * scale)),
                    max(1, round(source_h * scale)),
                )

            else:

                target_size = visual_size_pixels(
                    profile,
                    TILE_SIZE,
                )

            # -----------------------------------------------
            # FIT ALL ANIMATIONS
            # -----------------------------------------------

            display_animations = self._fit_enemy_animations(
                animations,
                target_size,
            )

            if not display_animations:

                print(
                    "WARNING: No display frames produced:",
                    enemy_id,
                )

                continue

            preview_frames = (
                display_animations.get("idle")
                or next(iter(display_animations.values()))
            )

            # -----------------------------------------------
            # REGISTER ENEMY ASSET
            # -----------------------------------------------

            asset = Asset(
                id=enemy_id,
                name=enemy_name,
                image=preview_frames[0],
                category="ENEMIES",
                object_class=Enemy,
                width=target_size[0],
                height=target_size[1],
                animations=display_animations,
                profile=profile,
            )

            asset.enemy_id = enemy_id

            asset.lethal = bool(
                definition.get("lethal", True)
            )

            self.register_asset(asset)

            print(
                "ENEMY PROFILE:",
                enemy_id,
                "visual_size=",
                target_size,
                "anchor=",
                profile.get("anchor"),
            )

        print(
            "REGISTERED ENEMIES:",
            [
                asset.id
                for asset in self.get_by_category("ENEMIES")
            ],
        )

    # ========================================================
    # END OBJECT
    # ========================================================

    def load_end(self):

        path = os.path.join(
            ITEMS,
            "Checkpoints",
            "End",
            "End (Idle)(1).png",
        )

        if not os.path.exists(path):
            return

        image = self.load_image(path)

        image = p.transform.scale(
            image,
            (TILE_SIZE, TILE_SIZE),
        )

        pressed_path = os.path.join(
            ITEMS,
            "Checkpoints",
            "End",
            "End (Pressed) (64x64).png",
        )

        if os.path.exists(pressed_path):

            pressed_image = self.load_image(
                pressed_path
            )

            if (
                pressed_image.get_width() >= 64
                and pressed_image.get_height() >= 64
            ):

                pressed_image = pressed_image.subsurface(
                    p.Rect(0, 0, 64, 64)
                ).copy()

            pressed_image = p.transform.scale(
                pressed_image,
                (TILE_SIZE, TILE_SIZE),
            )

        else:
            pressed_image = image.copy()

        asset = Asset(
            id="end",
            name="End",
            image=image,
            category="LEVEL",
            object_class=End,
            width=TILE_SIZE,
            height=TILE_SIZE,
        )

        self.register_asset(asset)

        asset.pressed_image = pressed_image

    # ========================================================
    # BACKGROUNDS
    # ========================================================

    def load_backgrounds(self):

        if not os.path.exists(BACKGROUND):
            return

        for filename in os.listdir(BACKGROUND):

            if not filename.lower().endswith(".png"):
                continue

            path = os.path.join(
                BACKGROUND,
                filename,
            )

            image = self.load_image(path)

            name = os.path.splitext(filename)[0]

            asset = Asset(
                id=f"background_{self.make_id(name)}",
                name=name,
                image=image,
                category="BACKGROUNDS",
                object_class=None,
                width=image.get_width(),
                height=image.get_height(),
            )

            self.register_asset(asset)

    # ========================================================
    # OTHER EFFECTS
    # ========================================================

    def load_other_assets(self):

        if not os.path.exists(OTHER):
            return

        for filename in os.listdir(OTHER):

            if not filename.lower().endswith(".png"):
                continue

            path = os.path.join(
                OTHER,
                filename,
            )

            image = self.load_image(path)

            image = p.transform.scale(
                image,
                (TILE_SIZE, TILE_SIZE),
            )

            name = os.path.splitext(filename)[0]

            asset = Asset(
                id=self.make_id(name),
                name=name,
                image=image,
                category="EFFECTS",
                object_class=None,
                width=TILE_SIZE,
                height=TILE_SIZE,
            )

            self.register_asset(asset)

    # ========================================================
    # MASTER LOADER
    # ========================================================

    def load_all(self):
        """Load all asset categories and return the asset registry."""

        self.assets.clear()

        self.load_blocks()
        self.load_characters()
        self.load_traps()
        self.load_fruits()
        self.load_collection_effect()
        self.load_boxes()
        self.load_checkpoint()
        self.load_start()
        self.load_end()
        self.load_backgrounds()
        self.load_enemies()
        self.load_other_assets()

        print(
            "ASSET CATEGORIES:",
            self.get_categories(),
        )

        print(
            "TOTAL ASSETS:",
            len(self.assets),
        )

        return self.assets
