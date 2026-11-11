import pygame
from pixelbound_core.config.constants import TILE_SIZE
from editor.config import screen_width
def mouse(screen):
    mouse_x,mouse_y=pygame.mouse.get_pos()
    tile_x=mouse_x//TILE_SIZE
    tile_y=mouse_y//TILE_SIZE
    highlight_x = tile_x * TILE_SIZE
    highlight_y = tile_y * TILE_SIZE
    if(highlight_x<(screen_width-50)):
     pygame.draw.rect(
     screen,
     (255,255,255),
     (highlight_x,
     highlight_y,
     TILE_SIZE,
     TILE_SIZE),
    4
)
    