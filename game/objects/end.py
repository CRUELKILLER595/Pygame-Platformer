import pygame as p

from .object import Object


END_IDLE_PATH = (
    "assets/Items/Checkpoints/"
    "End/End (Idle)(1).png"
)

END_PRESSED_PATH = (
    "assets/Items/Checkpoints/"
    "End/End (Pressed) (64x64)(1).png"
)


class End(Object):

    def __init__(
        self,
        x,
        y,
        width=64,
        height=64
    ):

        super().__init__(
            x,
            y,
            width,
            height,
            "end"
        )

        idle_image = p.image.load(
            END_IDLE_PATH
        ).convert_alpha()

        pressed_image = p.image.load(
            END_PRESSED_PATH
        ).convert_alpha()

        self.idle_image = p.transform.scale(
            idle_image,
            (width, height)
        )

        self.pressed_image = p.transform.scale(
            pressed_image,
            (width, height)
        )

        self.image = self.idle_image

        self.completed = False

    def complete(self):

        self.completed = True
        self.image = self.pressed_image

    def reset(self):

        self.completed = False
        self.image = self.idle_image