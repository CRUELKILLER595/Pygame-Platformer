import os
import re
import pygame as p

from .animation_loader import load_animation_sheet

from editor.tile_loader import (
    load_tiles,
    load_characterTile
)

from game.settings import TILE_SIZE

from game.objects.player import Player
from game.objects.Block import Block
from game.objects.fire import Fire
from game.objects.checkpoint import Checkpoint
from game.objects.start import Start
from game.objects.end import End
from game.objects.fruit import Fruit


ASSET_ROOT = "assets"

TERRAIN = os.path.join(
    ASSET_ROOT,
    "Terrain",
    "Terrain.png"
)

CHARACTERS = os.path.join(
    ASSET_ROOT,
    "MainCharacters"
)

TRAPS = os.path.join(
    ASSET_ROOT,
    "Traps"
)

ITEMS = os.path.join(
    ASSET_ROOT,
    "Items"
)

OTHER = os.path.join(
    ASSET_ROOT,
    "Other"
)

BACKGROUND = os.path.join(
    ASSET_ROOT,
    "Background"
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


# These are the sheets whose frame dimensions
# cannot reliably be inferred from their filenames.
TRAP_FRAME_SIZES = {

    "fire": {
        "on": (16, 32),
        "off": (16, 32),
        "hit": (32, 32),
    },

    "fan": {
        "on": (24, 8),
        "off": (24, 8),
    },

    "falling platforms": {
        "on": (32, 10),
        "off": (32, 10),
    },

    "saw": {
        "on": (38, 38),
        "off": (38, 38),
    },
}


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
        score_value=0
    ):

        self.id = id
        self.name = name
        self.image = image

        self.category = category

        self.width = width
        self.height = height

        self.object_class = object_class

        self.animations = animations or {}

        self.score_value = score_value

        self.palette_rect = None


class AssetManager:

    def __init__(self):

        self.assets = {}


    # --------------------------------------------------
    # Asset Registry
    # --------------------------------------------------

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

        return sorted(
            set(
                asset.category
                for asset in self.assets.values()
            )
        )


    # --------------------------------------------------
    # Utility
    # --------------------------------------------------

    @staticmethod
    def load_image(path):

        return p.image.load(
            path
        ).convert_alpha()


    @staticmethod
    def make_id(name):

        name = name.lower()

        name = re.sub(
            r"[^a-z0-9]+",
            "_",
            name
        )

        return name.strip("_")


    @staticmethod
    def parse_frame_size(filename):

        match = re.search(
            r"(\d+)\s*x\s*(\d+)",
            filename.lower()
        )

        if match:

            return (
                int(match.group(1)),
                int(match.group(2))
            )

        return None


    # --------------------------------------------------
    # Terrain
    # --------------------------------------------------

    def load_blocks(self):

        image = self.load_image(
            TERRAIN
        )

        tiles = load_tiles(
            image
        )

        for tile, row, col in tiles:

            asset = Asset(
                id=f"terrain_{row}_{col}",
                name=f"Terrain {row},{col}",
                image=tile,
                category="TILES",
                object_class=Block,
                width=TILE_SIZE,
                height=TILE_SIZE
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Characters
    # --------------------------------------------------

    def load_characters(self):

        if not os.path.exists(CHARACTERS):
            return

        for character in os.listdir(
            CHARACTERS
        ):

            folder = os.path.join(
                CHARACTERS,
                character
            )

            if not os.path.isdir(folder):
                continue

            idle_path = os.path.join(
                folder,
                "idle.png"
            )

            if not os.path.exists(
                idle_path
            ):
                continue

            image = self.load_image(
                idle_path
            )

            image = load_characterTile(
                image
            )

            asset = Asset(
                id=self.make_id(character),
                name=character,
                image=image,
                category="CHARACTERS",
                object_class=Player,
                width=TILE_SIZE,
                height=TILE_SIZE
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Trap Helpers
    # --------------------------------------------------

    def get_trap_frame_size(
        self,
        trap_name,
        animation_name
    ):

        trap_key = trap_name.lower()

        animation_key = (
            animation_name
            .lower()
            .strip()
        )

        # Explicit configuration first
        if trap_key in TRAP_FRAME_SIZES:

            size = TRAP_FRAME_SIZES[
                trap_key
            ].get(
                animation_key
            )

            if size:
                return size

        # Otherwise try dimensions in filename
        return self.parse_frame_size(
            animation_name
        )


    def get_trap_preview_file(
        self,
        files
    ):

        # Preferred states
        preferred = [
            "idle",
            "off",
            "on"
        ]

        for preferred_name in preferred:

            for filename in files:

                stem = os.path.splitext(
                    filename
                )[0].lower()

                if stem.startswith(
                    preferred_name
                ):

                    return filename

        # Fallback
        for filename in files:

            if filename.lower().endswith(
                ".png"
            ):

                return filename

        return None


    # --------------------------------------------------
    # Traps
    # --------------------------------------------------

    def load_traps(self):

        if not os.path.exists(
            TRAPS
        ):
            return

        for trap_name in os.listdir(
            TRAPS
        ):

            trap_path = os.path.join(
                TRAPS,
                trap_name
            )

            if not os.path.isdir(
                trap_path
            ):
                continue

            files = os.listdir(
                trap_path
            )

            png_files = [
                file
                for file in files
                if file.lower().endswith(
                    ".png"
                )
            ]

            if not png_files:
                continue

            animations = {}

            for filename in png_files:

                animation_path = os.path.join(
                    trap_path,
                    filename
                )

                animation_name = (
                    os.path.splitext(
                        filename
                    )[0]
                )

                image = self.load_image(
                    animation_path
                )

                frame_size = (
                    self.get_trap_frame_size(
                        trap_name,
                        animation_name
                    )
                )

                if frame_size:

                    frame_width, frame_height = (
                        frame_size
                    )

                    frames = load_animation_sheet(
                        animation_path,
                        frame_width,
                        frame_height
                    )

                else:

                    # Static image
                    frame = p.transform.scale(
                        image,
                        (
                            TILE_SIZE,
                            TILE_SIZE
                        )
                    )

                    frames = [frame]

                animations[
                    animation_name.lower()
                ] = frames

            preview_file = (
                self.get_trap_preview_file(
                    png_files
                )
            )

            if preview_file is None:
                continue

            preview_name = (
                os.path.splitext(
                    preview_file
                )[0]
                .lower()
            )

            preview_frames = animations.get(
                preview_name
            )

            if not preview_frames:

                preview_frames = [
                    p.transform.scale(
                        self.load_image(
                            os.path.join(
                                trap_path,
                                preview_file
                            )
                        ),
                        (
                            TILE_SIZE,
                            TILE_SIZE
                        )
                    )
                ]

            preview = preview_frames[0]

            # Trap classes other than Fire do not
            # exist yet, so we keep object_class=None.
            #
            # We will connect each class as we create it.
            object_class = None

            if trap_name.lower() == "fire":
                object_class = Fire

            asset = Asset(
                id=self.make_id(
                    trap_name
                ),
                name=trap_name,
                image=preview,
                category="TRAPS",
                object_class=object_class,
                width=TILE_SIZE,
                height=TILE_SIZE,
                animations=animations
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Fruits / Collectibles
    # --------------------------------------------------

    def load_fruits(self):

        path = os.path.join(
            ITEMS,
            "Fruits"
        )

        if not os.path.exists(path):
            return
        collected_path = os.path.join(
            path,
            "Collected.png"
        )

        collected_frames = []

        if os.path.exists(collected_path):

            collected_frames = load_animation_sheet(
                collected_path,
                32,
                32
            )

        for filename in os.listdir(
            path
        ):

            if not filename.lower().endswith(
                ".png"
            ):
                continue

            if filename.lower() == "collected.png":
                continue

            fruit_name = os.path.splitext(
                filename
            )[0]

            image_path = os.path.join(
                path,
                filename
            )

            frames = load_animation_sheet(
                image_path,
                32,
                32
            )

            score = FRUIT_SCORES.get(
                fruit_name,
                100
            )

            asset = Asset(
                id=self.make_id(
                    fruit_name
                ),
                name=fruit_name,
                image=frames[0],
                category="COLLECTIBLES",
                object_class=Fruit,
                width=TILE_SIZE,
                height=TILE_SIZE,
                animations={
                    "idle": frames,
                    "collected":collected_frames
                },
                score_value=score
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Collection Effect
    # --------------------------------------------------

    def load_collection_effect(self):

        path = os.path.join(
            ITEMS,
            "Fruits",
            "Collected.png"
        )

        if not os.path.exists(path):
            return

        frames = load_animation_sheet(
            path,
            32,
            32
        )

        asset = Asset(
            id="collected_effect",
            name="Collected",
            image=frames[0],
            category="EFFECTS",
            object_class=None,
            width=TILE_SIZE,
            height=TILE_SIZE,
            animations={
                "collected": frames
            }
        )

        self.register_asset(
            asset
        )


    # --------------------------------------------------
    # Boxes
    # --------------------------------------------------

    def load_boxes(self):

        path = os.path.join(
            ITEMS,
            "Boxes"
        )

        if not os.path.exists(path):
            return

        for box_name in os.listdir(
            path
        ):

            box_path = os.path.join(
                path,
                box_name
            )

            if not os.path.isdir(
                box_path
            ):
                continue

            idle_path = None

            for filename in os.listdir(
                box_path
            ):

                if filename.lower() == "idle.png":

                    idle_path = os.path.join(
                        box_path,
                        filename
                    )

                    break

            if idle_path is None:
                continue

            image = self.load_image(
                idle_path
            )

            image = p.transform.scale(
                image,
                (
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

            animations = {}

            for filename in os.listdir(
                box_path
            ):

                if not filename.lower().endswith(
                    ".png"
                ):
                    continue

                file_path = os.path.join(
                    box_path,
                    filename
                )

                frame_size = self.parse_frame_size(
                    filename
                )

                animation_name = (
                    os.path.splitext(
                        filename
                    )[0]
                    .lower()
                )

                if frame_size:

                    frames = load_animation_sheet(
                        file_path,
                        *frame_size
                    )

                else:

                    image = self.load_image(
                        file_path
                    )

                    image = p.transform.scale(
                        image,
                        (
                            TILE_SIZE,
                            TILE_SIZE
                        )
                    )

                    frames = [image]

                animations[
                    animation_name
                ] = frames

            asset = Asset(
                id=self.make_id(
                    box_name
                ),
                name=box_name,
                image=image,
                category="BREAKABLES",
                object_class=None,
                width=TILE_SIZE,
                height=TILE_SIZE,
                animations=animations
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Level Objects
    # --------------------------------------------------

    def load_checkpoint(self):

        path = os.path.join(
            ITEMS,
            "Checkpoints",
            "Checkpoint",
            "Checkpoint (No Flag).png"
        )

        if not os.path.exists(path):
            return

        image = self.load_image(
            path
        )

        image = p.transform.scale(
            image,
            (
                TILE_SIZE,
                TILE_SIZE
            )
        )

        asset = Asset(
            id="checkpoint",
            name="Checkpoint",
            image=image,
            category="LEVEL",
            object_class=Checkpoint,
            width=TILE_SIZE,
            height=TILE_SIZE
        )

        self.register_asset(
            asset
        )


    def load_start(self):

        path = os.path.join(
            ITEMS,
            "Checkpoints",
            "Start",
            "Start (Idle)(1).png"
        )

        if not os.path.exists(path):
            return

        image = self.load_image(
            path
        )

        image = p.transform.scale(
            image,
            (
                TILE_SIZE,
                TILE_SIZE
            )
        )

        asset = Asset(
            id="start",
            name="Start",
            image=image,
            category="LEVEL",
            object_class=Start,
            width=TILE_SIZE,
            height=TILE_SIZE
        )

        self.register_asset(
            asset
        )


    def load_end(self):

        path = os.path.join(
            ITEMS,
            "Checkpoints",
            "End",
            "End (Idle)(1).png"
        )

        if not os.path.exists(path):
            return

        image = self.load_image(
            path
        )

        image = p.transform.scale(
            image,
            (
                TILE_SIZE,
                TILE_SIZE
            )
        )
        pressed_path = os.path.join(
    ITEMS,
    "Checkpoints",
    "End",
    "End (Pressed) (64x64).png"
)

        pressed_image = self.load_image(
    pressed_path
)

        pressed_image = pressed_image.subsurface(
    p.Rect(
        0,
        0,
        64,
        64
    )
).copy()

        pressed_image = p.transform.scale(
    pressed_image,
    (
        TILE_SIZE,
        TILE_SIZE
    )
)

        asset = Asset(
            id="end",
            name="End",
            image=image,
            category="LEVEL",
            object_class=End,
            width=TILE_SIZE,
            height=TILE_SIZE
        )

        self.register_asset(
            asset
        )
        asset.pressed_image=pressed_image


    # --------------------------------------------------
    # Backgrounds
    # --------------------------------------------------

    def load_backgrounds(self):

        if not os.path.exists(
            BACKGROUND
        ):
            return

        for filename in os.listdir(
            BACKGROUND
        ):

            if not filename.lower().endswith(
                ".png"
            ):
                continue

            path = os.path.join(
                BACKGROUND,
                filename
            )

            image = self.load_image(
                path
            )

            name = os.path.splitext(
                filename
            )[0]

            asset = Asset(
                id=f"background_{self.make_id(name)}",
                name=name,
                image=image,
                category="BACKGROUNDS",
                object_class=None,
                width=image.get_width(),
                height=image.get_height()
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Other
    # --------------------------------------------------

    def load_other_assets(self):

        if not os.path.exists(
            OTHER
        ):
            return

        for filename in os.listdir(
            OTHER
        ):

            if not filename.lower().endswith(
                ".png"
            ):
                continue

            path = os.path.join(
                OTHER,
                filename
            )

            image = self.load_image(
                path
            )

            image = p.transform.scale(
                image,
                (
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

            name = os.path.splitext(
                filename
            )[0]

            asset = Asset(
                id=self.make_id(name),
                name=name,
                image=image,
                category="EFFECTS",
                object_class=None,
                width=TILE_SIZE,
                height=TILE_SIZE
            )

            self.register_asset(
                asset
            )


    # --------------------------------------------------
    # Master Loader
    # --------------------------------------------------

    def load_all(self):

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

        self.load_other_assets()

        print("ASSET CATEGORIES:", self.get_categories())
        print("TOTAL ASSETS:", len(self.assets))

        return self.assets