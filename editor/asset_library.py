import pygame
import os
from .tile_loader import (
    load_tiles,
    load_characterTile
)

from game.objects.object import Object
from game.objects.player import Player
from game.objects.Block import Block
from game.objects.fire import Fire
from game.objects.checkpoint import Checkpoint
from game.objects.start import Start
from game.objects.end import End

from game.settings import TILE_SIZE


Assets = {}


class Asset:

    def __init__(
        self,
        id,
        name,
        image,
        category,
        object_class,
        width,
        height
    ):

        self.id = id
        self.name = name
        self.image = image
        self.category = category
        self.width = width
        self.height = height
        self.object_class = object_class

        self.palette_rect = None


def register_asset(asset):

    Assets[asset.id] = asset


def load_image(path):

    return pygame.image.load(
        path
    ).convert_alpha()


def load_blocks():

    image = pygame.image.load(
        "assets/Terrain/Terrain.png"
    ).convert_alpha()

    tiles = load_tiles(image)

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

        register_asset(asset)


def load_character():

    path = "assets/MainCharacters"

    for character in os.listdir(path):

        folder = os.path.join(
            path,
            character
        )

        image = pygame.image.load(
            os.path.join(
                folder,
                "idle.png"
            )
        ).convert_alpha()

        img = load_characterTile(
            image
        )

        asset = Asset(
            id=character.lower(),
            name=character,
            image=img,
            category="CHARACTERS",
            object_class=Player,
            width=TILE_SIZE,
            height=TILE_SIZE
        )

        register_asset(asset)


def load_fire():

    image = load_image(
        "assets/Traps/Fire/on.png"
    )
    frame = image.subsurface(
        pygame.Rect(0, 0, 16, 32)
    ).copy()
    frame = pygame.transform.scale(
        frame,
        (TILE_SIZE, TILE_SIZE)
    )

    asset = Asset(
        id="fire",
        name="Fire",
        image=frame,
        category="TRAPS",
        object_class=Fire,
        width=TILE_SIZE,
        height=TILE_SIZE
    )

    register_asset(asset)


def load_checkpoint():

    image = load_image(
        "assets/Items/Checkpoints/"
        "Checkpoint/Checkpoint (No Flag).png"
    )
    image=pygame.transform.scale(
        image,
        (TILE_SIZE,TILE_SIZE)
    )

    asset = Asset(
        id="checkpoint",
        name="Checkpoint",
        image=image,
        category="LEVEL",
        object_class=Checkpoint,
        width=image.get_width(),
        height=image.get_height()
    )

    register_asset(asset)


def load_start():

    image = load_image(
        "assets/Items/Checkpoints/"
        "Start/Start (Idle)(1).png"
    )
    image=pygame.transform.scale(
            image,
            (TILE_SIZE,TILE_SIZE)
        )

    asset = Asset(
        id="start",
        name="Start",
        image=image,
        category="LEVEL",
        object_class=Start,
        width=image.get_width(),
        height=image.get_height()
    )

    register_asset(asset)


def load_end():

    image = load_image(
        "assets/Items/Checkpoints/"
        "End/End (Idle)(1).png"
    )
    image=pygame.transform.scale(
            image,  
            (TILE_SIZE,TILE_SIZE)
        )

    asset = Asset(
        id="end",
        name="End",
        image=image,
        category="LEVEL",
        object_class=End,
        width=image.get_width(),
        height=image.get_height()
    )

    register_asset(asset)


def load_backgrounds():

    backgrounds = [
        "Blue",
        "Brown",
        "Gray",
        "Green",
        "Pink",
        "Purple",
        "Yellow"
    ]

    for name in backgrounds:

        path = (
            "assets/Background/"
            f"{name}.png"
        )

        if not os.path.exists(path):
            continue

        image = load_image(path)

        asset = Asset(
            id=f"background_{name.lower()}",
            name=name,
            image=image,
            category="BACKGROUNDS",
            object_class=None,
            width=image.get_width(),
            height=image.get_height()
        )

        register_asset(asset)


def get_categories():

    return sorted(
        set(
            asset.category
            for asset in Assets.values()
        )
    )


def load_assets():

    Assets.clear()

    load_character()
    load_blocks()

    load_fire()
    load_start()
    load_checkpoint()
    load_end()

    load_backgrounds()
    get_categories()

    return Assets

     
     
     
     
        

   


        