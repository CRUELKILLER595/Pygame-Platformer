import pygame as p
p.init()
class Action:
    def __init__(self, position, old_asset, new_asset):
        self.position = position
        self.old_asset = old_asset
        self.new_asset = new_asset
    