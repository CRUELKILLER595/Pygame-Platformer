import pygame as p

from .object import Object


CHECKPOINT_IDLE_PATH = (
    "assets/Items/Checkpoints/"
    "Checkpoint/Checkpoint (No Flag).png"
)

CHECKPOINT_ACTIVE_PATH = (
    "assets/Items/Checkpoints/"
    "Checkpoint/Checkpoint (Flag Idle)(64x64).png"
)


class Checkpoint(Object):

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
            "checkpoint"
        )

        idle_image = p.image.load(
            CHECKPOINT_IDLE_PATH
        ).convert_alpha()

        active_image = p.image.load(
            CHECKPOINT_ACTIVE_PATH
        ).convert_alpha()

        self.idle_image = p.transform.scale(
            idle_image,
            (width, height)
        )

        self.active_image = p.transform.scale(
            active_image,
            (width, height)
        )

        self.image = self.idle_image

        self.active = False

    def activate(self):

        self.active = True
        self.image = self.active_image

    def reset(self):

        self.active = False
        self.image = self.idle_image