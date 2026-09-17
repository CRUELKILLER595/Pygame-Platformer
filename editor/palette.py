import pygame
from game.settings import screen_height, side_margin
pygame.init()

class Palette:
    def __init__(self, assets, x, y, width,category):
        self.assets = assets
        self.x = x
        self.y = y
        self.width = width
        self.category=category
        self.filtered_assets = [
    asset for asset in self.assets.values()
    if asset.category == self.category
]
        self.dragged_asset=None

    def draw_palette(self, screen):
     pygame.draw.rect(
        screen,
        (25, 40, 65),
        (self.x, self.y, self.width, screen_height*0.9)
    )
     self.filtered_assets = [
    asset for asset in self.assets.values()
    if asset.category == self.category
]

     columns = 2
     padding = 10
     spacing = 10

     start_x = self.x + padding
     start_y = self.y + padding

     

     for index, asset in enumerate(self.filtered_assets):

       column = index % columns
       row = index // columns

       x = start_x + column * (asset.width + spacing)
       y = start_y + row * (asset.height + spacing)

       screen.blit(asset.image, (x, y))

       asset.palette_rect = pygame.Rect(
        x,
        y,
        asset.width,
        asset.height
    )
       print(asset.palette_rect)
    def get_clicked_asset(self,mouse_pos):
     for asset in self.filtered_assets:
       if asset.palette_rect.collidepoint(mouse_pos):
         return asset
     return None
         
