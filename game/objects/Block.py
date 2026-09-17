import pygame


class Block(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
        size,
        image
    ):

        super().__init__()

        self.rect = pygame.Rect(
            x,
            y,
            size,
            size
        )

        # Use the exact image from the Asset Library.
        # This makes editor and game use the same tile.
        if image.get_size() != (size, size):

            self.image = pygame.transform.scale(
                image,
                (size, size)
            )

        else:

            self.image = image

        self.mask = pygame.mask.from_surface(
            self.image
        )

    def draw(self, win, offset_x):

        win.blit(
            self.image,
            (
                self.rect.x - offset_x,
                self.rect.y
            )
        )