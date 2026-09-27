import pygame as p
from .object import Object
class Collectible(Object):
    def __init__(self,x,y,width,height,image):
         super().__init__(
            x,
            y,
            width,
            height,
            "collectible"
        )

         self.image = image
         self.collected = False
    def collect(self):

        if self.collected:
            return

        self.collected = True

    def update(self):
        pass