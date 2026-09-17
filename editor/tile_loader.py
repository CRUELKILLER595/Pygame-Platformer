import pygame as pygame

from game.settings import TILE_SIZE, SPRITE_SIZE


def load_tiles(terrain):

    rows = terrain.get_height() // SPRITE_SIZE
    cols = terrain.get_width() // SPRITE_SIZE

    print(
        "Terrain size:",
        terrain.get_width(),
        terrain.get_height()
    )

    print("Rows:", rows)
    print("Cols:", cols)

    tiles = []

    for row in range(rows):

        for col in range(cols):

            # Source rectangle.
            # Terrain artwork uses SPRITE_SIZE pixels
            # per source tile.
            rect = pygame.Rect(
                col * SPRITE_SIZE,
                row * SPRITE_SIZE,
                SPRITE_SIZE,
                SPRITE_SIZE
            )

            tile = terrain.subsurface(
                rect
            ).copy()

            # Convert source tile size into
            # the game's editor/world tile size.
            tile = pygame.transform.scale(
                tile,
                (TILE_SIZE, TILE_SIZE)
            )

            tiles.append(
                (tile, row, col)
            )

    return tiles


def load_characterTile(character):

    height = character.get_height()

    width = character.get_width() // 11

    rect = pygame.Rect(
        0,
        0,
        width,
        height
    )

    tile = pygame.Surface(
        (width, height),
        pygame.SRCALPHA
    )

    tile.blit(
        character,
        (0, 0),
        rect
    )

    tile = pygame.transform.scale(
        tile,
        (TILE_SIZE, TILE_SIZE)
    )

    return tile
    

    



    
