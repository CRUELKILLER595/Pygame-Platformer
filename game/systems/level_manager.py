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
from game.objects.fruit import Fruit
from game.systems.character_registry import DEFAULT_CHARACTER
from ..objects.trap import Trap
from .asset_manager import Asset,AssetManager


class LevelManager:

    def __init__(self,asset_manager):
        self.asset_manager=asset_manager

    def load_level(
        self,
        level_path,character_id=DEFAULT_CHARACTER
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

           

            grid_x = int(data["x"])
            grid_y = int(data["y"])

            x = grid_x * TILE_SIZE
            y = grid_y * TILE_SIZE

            asset = self.asset_manager.get(asset_id)

            if asset is None:

                print(
                    "WARNING: Asset not found:",
                    asset_id
                )

                continue

          

            if asset.object_class == Player:

                # Only one playable player is allowed.
                if player is not None:

                    print(
                        "WARNING: Extra player spawn ignored:",
                        asset_id,
                        "at",
                        (grid_x, grid_y)
                    )

                    continue

                player = Player(
    x,
    y,
    asset.width,
    asset.height,
    character_id=character_id
)

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
        asset.image,
        asset.pressed_image
    )

            # ==================================================
            # GENERIC OBJECT
            # ==================================================

            elif asset.object_class == Object:

                obj = Object(
                    x,
                    y,
                    asset.width,
                    asset.height,
                    asset.name
                )
            
# --------------------------------------------------
# TRAPS
# --------------------------------------------------

            elif asset.category == "TRAPS":

                if asset.object_class is Fire:
        # Keep the existing Fire implementation.
                 obj = Fire(
            x,
            y,
            asset.width,
            asset.height,
        )
                 obj.on()

                else:
        
                   obj = Trap(x, y, asset)

                   objects.append(obj)


                obj.image = asset.image
            elif asset.object_class==Fruit:
                obj=Fruit(
                    x,
                    y,
                    asset,
                    asset.name
                )
            

            # ==================================================
            # UNKNOWN
            # ==================================================

            else:

                print(
                    "WARNING: Unknown object class:",
                    asset.object_class
                )

                continue

            objects.append(
                obj
            )

        if player is None:

            print(
                "WARNING: Level has no player spawn!"
            )

        return player, objects