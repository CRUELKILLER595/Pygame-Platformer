import pygame as p


class TiledBackground:

    def __init__(self, image_path):

        self.image = p.image.load(
            image_path
        ).convert_alpha()

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, screen):

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        for x in range(
            0,
            screen_width,
            self.width
        ):

            for y in range(
                0,
                screen_height,
                self.height
            ):

                screen.blit(
                    self.image,
                    (x, y)
                )