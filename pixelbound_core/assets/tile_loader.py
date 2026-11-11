

import pygame


def load_tiles(
    terrain: pygame.Surface,
    *,
    tile_size: int,
    sprite_size: int,
) -> list[tuple[pygame.Surface, int, int]]:

    if tile_size <= 0 or sprite_size <= 0:
        raise ValueError("Tile sizes must be positive.")

    rows = terrain.get_height() // sprite_size
    cols = terrain.get_width() // sprite_size

    print("Terrain size:", terrain.get_width(), terrain.get_height())
    print("Rows:", rows)
    print("Cols:", cols)

    tiles = []

    for row in range(rows):
        for col in range(cols):

            rect = pygame.Rect(
                col * sprite_size,
                row * sprite_size,
                sprite_size,
                sprite_size,
            )

            tile = terrain.subsurface(rect).copy()

            tile = pygame.transform.scale(
                tile,
                (tile_size, tile_size),
            )

            tiles.append((tile, row, col))

    return tiles


def load_character_tile(
    character: pygame.Surface,
    *,
    tile_size: int,
    frames_per_sheet: int = 11,
) -> pygame.Surface:

    if tile_size <= 0 or frames_per_sheet <= 0:
        raise ValueError("Tile size and frame count must be positive.")

    height = character.get_height()
    width = character.get_width() // frames_per_sheet

    if width <= 0 or height <= 0:
        raise ValueError("Invalid character sprite sheet dimensions.")

    rect = pygame.Rect(0, 0, width, height)

    tile = pygame.Surface(
        (width, height),
        pygame.SRCALPHA,
    )

    tile.blit(character, (0, 0), rect)

    return pygame.transform.scale(
        tile,
        (tile_size, tile_size),
    )


    



    
