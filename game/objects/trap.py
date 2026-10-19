
import pygame as p

from .object import Object


class Trap(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, asset):
        super().__init__(
            x,
            y,
            asset.width,
            asset.height,
            asset.name,
        )

        self.asset_id = asset.id
        self.animation_count = 0
        self.animations = {}

        # Scale the loaded frames to the asset's configured size.
        for name, frames in getattr(
            asset, "animations", {}
        ).items():
            if not frames:
                continue

            self.animations[name.lower()] = [
                p.transform.scale(
                    frame,
                    (asset.width, asset.height),
                )
                if frame.get_size() != (
                    asset.width, asset.height
                )
                else frame
                for frame in frames
            ]

        # Pick an appropriate initial animation.
        self.animation_name = next(
            (
                name
                for name in ("idle", "on", "off")
                if name in self.animations
            ),
            next(iter(self.animations), ""),
        )

        frames = self.animations.get(
            self.animation_name, []
        )

        if frames:
            self.image = frames[0]
        else:
            self.image = p.transform.scale(
                asset.image,
                (asset.width, asset.height),
            )

        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = p.mask.from_surface(self.image)

    def loop(self):
        frames = self.animations.get(
            self.animation_name, []
        )

        if not frames:
            return

        frame_index = (
            self.animation_count // self.ANIMATION_DELAY
        ) % len(frames)

        position = self.rect.topleft
        self.image = frames[frame_index]
        self.rect = self.image.get_rect(topleft=position)
        self.mask = p.mask.from_surface(self.image)

        self.animation_count += 1

    def draw(self, win, offset_x=0):
        win.blit(
            self.image,
            (
                int(self.rect.x - offset_x),
                int(self.rect.y),
            ),
        )
