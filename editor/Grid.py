import pygame as py
py.init()

from game.settings import TILE_SIZE, side_margin


def draw_grid(screen, camera):
    start_x = (camera.x // TILE_SIZE) * TILE_SIZE
    start_y = (camera.y // TILE_SIZE) * TILE_SIZE

    x = start_x

    while x <= camera.x + camera.width:
        screen_x, _ = camera.world_to_screen(x, 0)

        py.draw.line(
            screen,
            (60, 60, 60),
            (screen_x, 0),
            (screen_x, camera.height)
        )

        x += TILE_SIZE

    y = start_y

    while y <= camera.y + camera.height:
        _, screen_y = camera.world_to_screen(0, y)

        py.draw.line(
            screen,
            (60, 60, 60),
            (0, screen_y),
            (camera.width, screen_y)
        )

        y += TILE_SIZE
    
    
