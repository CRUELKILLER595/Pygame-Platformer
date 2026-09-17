import json

from editor.asset_library import load_assets

from game.settings import TILE_SIZE

from game.objects.player import Player
from game.objects.Block import Block
from game.objects.fire import Fire
from game.objects.checkpoint import Checkpoint
from game.objects.start import Start
from game.objects.end import End
from game.objects.object import Object


class LevelManager:

    def __init__(self):

        self.assets = load_assets()

    def load_level(
        self,
        level_path
    ):

        with open(
            level_path,
            "r"
        ) as file:

            level_data = json.load(file)

        objects = []
        player = None

        for data in level_data["objects"]:

            asset_id = data["id"]

            x = (
                data["x"] *
                TILE_SIZE
            )

            y = (
                data["y"] *
                TILE_SIZE
            )

            asset = self.assets.get(
                asset_id
            )

            if asset is None:

                print(
                    "WARNING: Asset not found:",
                    asset_id
                )

                continue

            if asset.object_class == Player:

                obj = Player(
                    x,
                    y,
                    asset.width,
                    asset.height
                )

                player = obj

                continue

            elif asset.object_class == Block:

                obj = Block(
                    x,
                    y,
                    asset.width,
                    asset.image
                )

            elif asset.object_class == Fire:

                obj = Fire(
                    x,
                    y,
                    asset.width,
                    asset.height
                )

                obj.on()

            elif asset.object_class == Checkpoint:

                obj = Checkpoint(
                    x,
                    y,
                    asset.width,
                    asset.height
                )

            elif asset.object_class == Start:

                obj = Start(
                    x,
                    y,
                    asset.width,
                    asset.height
                )

            elif asset.object_class == End:

                obj = End(
                    x,
                    y,
                    asset.width,
                    asset.height
                )

            elif asset.object_class == Object:

                obj = Object(
                    x,
                    y,
                    asset.width,
                    asset.height,
                    asset.name
                )

                obj.image = asset.image

            else:

                print(
                    "WARNING: Unknown object class:",
                    asset.object_class
                )

                continue

            objects.append(obj)

        return player, objects