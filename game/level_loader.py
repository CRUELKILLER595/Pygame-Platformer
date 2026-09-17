import pygame as p
import json
from editor.asset_library import load_assets
from .settings import TILE_SIZE

p.init()
ASSETS = load_assets()
def give_level():
 with open("levels/level1.json", "r") as file:
    level = json.load(file)
 placed_assets={}
 for obj in level["objects"]:
    asset = ASSETS[obj["id"]]
    placed_assets[(obj["x"], obj["y"])] = asset
 return placed_assets