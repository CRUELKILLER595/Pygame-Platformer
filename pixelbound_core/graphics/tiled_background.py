
from pathlib import Path

import pygame

from pixelbound_core.config.paths import PROJECT_ROOT


class TiledBackground:

    def __init__(self, image_path):

        image_path = Path(image_path)

        if not image_path.is_absolute():
            image_path = PROJECT_ROOT / image_path

        if not image_path.is_file():
            raise FileNotFoundError(
                f"Background image not found: {image_path}"
            )

        self.image = pygame.image.load(
            str(image_path)
        ).convert_alpha()

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, screen):

        if self.width <= 0 or self.height <= 0:
            return

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        for x in range(0, screen_width, self.width):
            for y in range(0, screen_height, self.height):

                screen.blit(
                    self.image,
                    (x, y),
                )
