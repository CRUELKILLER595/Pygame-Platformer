import pygame as p

from .object import Object


START_PATH = (
    "assets/Items/Checkpoints/"
    "Start/Start (Idle)(1).png"
)


class Start(Object):

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
            "start"
        )

        image = p.image.load(
            START_PATH
        ).convert_alpha()

        self.image = p.transform.scale(
            image,
            (width, height)
        )

    def get_spawn_position(
        self,
        player
    ):

        return (
            self.rect.centerx
            - player.rect.width // 2,

            self.rect.bottom
            - player.rect.height
        )