import pygame as p

from ..systems.collision_profiles import (
    DEBUG_HITBOXES,
    DEFAULT_TRAP_HITBOX,
    TRAP_HITBOX_PROFILES,
    make_collision_rect,
    profile_for,
)


class Hazard(p.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
        width,
        height,
        animations=None,
        name="hazard",
        image=None,
        collision_profile=None,
        animation_speed=4,
    ):
        super().__init__()

        self.name = str(name or "hazard")

        self.width = max(1, int(width))
        self.height = max(1, int(height))

        # Visual rectangle. Keep this aligned with the tile.
        self.rect = p.Rect(
            int(x),
            int(y),
            self.width,
            self.height
        )

        # Load and scale animation frames.
        self.animations = {}

        for key, frames in (animations or {}).items():
            valid_frames = [
                frame
                for frame in (frames or [])
                if isinstance(frame, p.Surface)
            ]

            if valid_frames:
                self.animations[str(key).lower()] = [
                    p.transform.scale(
                        frame,
                        (self.width, self.height)
                    )
                    for frame in valid_frames
                ]

        # Fallback for a static image.
        if not self.animations and image is not None:
            self.animations["idle"] = [
                p.transform.scale(
                    image,
                    (self.width, self.height)
                )
            ]

        self.animation_name = self._initial_animation()
        self.animation_index = 0
        self.animation_counter = 0

        self.animation_speed = max(
            1,
            int(animation_speed)
        )

        self.image = self._current_frame()

        # Collision rectangle. This is separate from self.rect.
        self.collision_profile = (
            collision_profile
            or profile_for(
                self.name,
                TRAP_HITBOX_PROFILES,
                DEFAULT_TRAP_HITBOX
            )
        )

        self.collision_rect = make_collision_rect(
            self.rect,
            self.collision_profile
        )

        # Alias for convenience.
        self.hitbox = self.collision_rect

        self.debug_hitbox = DEBUG_HITBOXES

    def _initial_animation(self):
        for key in (
            "on",
            "idle",
            "active",
            "default",
            "walk"
        ):
            if key in self.animations:
                return key

        return next(iter(self.animations), "idle")

    def _current_frame(self):
        frames = self.animations.get(
            self.animation_name,
            []
        )

        if frames:
            return frames[
                self.animation_index % len(frames)
            ]

        return p.Surface(
            (self.width, self.height),
            p.SRCALPHA
        )

    def set_animation(self, name):
        name = str(name or "").lower()

        aliases = {
            "on": ("idle", "active", "default"),
            "idle": ("on", "active", "default"),
            "off": ("idle", "on", "default"),
            "active": ("on", "idle", "default"),
        }

        if name not in self.animations:
            name = next(
                (
                    candidate
                    for candidate in aliases.get(name, ())
                    if candidate in self.animations
                ),
                self.animation_name
            )

        if name != self.animation_name:
            self.animation_name = name
            self.animation_index = 0
            self.animation_counter = 0
            self.image = self._current_frame()

    def on(self):
        self.set_animation("on")

    def off(self):
        self.set_animation("off")

    def loop(self):
        frames = self.animations.get(
            self.animation_name,
            []
        )

        if len(frames) > 1:
            self.animation_counter += 1

            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0

                self.animation_index = (
                    self.animation_index + 1
                ) % len(frames)

                self.image = frames[
                    self.animation_index
                ]

        # Recalculate in case the object's position changes.
        self.collision_rect = make_collision_rect(
            self.rect,
            self.collision_profile
        )

        self.hitbox = self.collision_rect

        return False

    def draw(self, win, offset_x=0):
        # Draw the full sprite, not the collision rectangle.
        win.blit(
            self.image,
            (
                int(self.rect.x - offset_x),
                int(self.rect.y)
            )
        )

        # Optional debug outline.
        if self.debug_hitbox:
            debug_rect = self.collision_rect.copy()
            debug_rect.x -= int(offset_x)

            p.draw.rect(
                win,
                (255, 0, 255),
                debug_rect,
                2
            )