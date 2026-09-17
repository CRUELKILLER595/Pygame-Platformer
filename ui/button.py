import pygame as py


class Button:

    def __init__(
        self,
        text=None,
        position=(0, 0),
        size=(100, 50),
        font=None,
        callback=None,
        image=None
    ):

        self.text = text

        self.x, self.y = position
        self.width, self.height = size

        self.font = font
        self.callback = callback
        self.image = image

        self.rect = py.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def draw(self, screen):

        # Draw the button background
        py.draw.rect(
            screen,
            (50, 50, 50),
            self.rect
        )

        # Image buttons take priority over text
        if self.image:

            image_rect = self.image.get_rect(
                center=self.rect.center
            )

            screen.blit(
                self.image,
                image_rect
            )

        elif self.text and self.font:

            text_surface = self.font.render(
                self.text,
                True,
                (0, 0, 255)
            )

            text_rect = text_surface.get_rect(
                center=self.rect.center
            )

            screen.blit(
                text_surface,
                text_rect
            )

    def handle_event(self, event):

        if event.type == py.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.rect.collidepoint(event.pos):

                    if self.callback:
                        self.callback()