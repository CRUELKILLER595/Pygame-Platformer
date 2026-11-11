
import re
import pygame as p
import random
from .animated_object import AnimatedObject


class Box(AnimatedObject):

    # Number of update calls between animation frames.
    ANIMATION_DELAY = 5

    def __init__(self, x, y, asset,fruit_assets=None):

     self.asset = asset
     self.name = asset.name

    # Normalise animation names before initialising
    # the parent AnimatedObject.
     self.box_animations = self._normalise_animations(
        getattr(asset, "animations", {})
    )

    # Fallback if no idle animation was loaded.
     if not self.box_animations.get("idle"):
         self.box_animations["idle"] = [asset.image]

    # AnimatedObject expects six arguments after self:
    # x, y, width, height, name, animations.
     super().__init__(
        x,
        y,
        asset.width,
        asset.height,
        asset.name,
        self.box_animations
    )

     idle_frame = self.box_animations["idle"][0]

     self.rect = p.Rect(
        int(x),
        int(y),
        idle_frame.get_width(),
        idle_frame.get_height()
    )

     self.current_animation = "idle"
     self.animation_name = "idle"
     self.animation_index = 0
     self.animation_count = 0

     self.image = idle_frame
     self.sprite = idle_frame

     self.hit_count = 0
     self.hits_to_break = max(
        1,
        int(getattr(asset, "hits_to_break", 1))
    )

     self.breaking = False
     self.broken = False
     self._after_hit = None
     # Random fruit reward assigned once to this box.
     self.reward_asset = (
     random.choice(fruit_assets)
    if fruit_assets
    else None
    
)
     self.reward_spawned = False

# Prevent the same box from spawning multiple fruits.
    @staticmethod
    def _normalise_animations(animations):

        normalised = {}

        for name, frames in animations.items():

            name = str(name).lower()

            # Remove frame-size annotations, such as "(28x24)".
            name = re.sub(
                r"\s*\(\s*\d+\s*x\s*\d+\s*\)",
                "",
                name
            ).strip()

            if name.startswith("idle"):
                action = "idle"

            elif name.startswith("hit"):
                action = "hit"

            elif name.startswith("break"):
                action = "break"

            else:
                continue

            if isinstance(frames, p.Surface):
                frames = [frames]

            elif not isinstance(frames, (list, tuple)):
                continue

            frames = [
                frame
                for frame in frames
                if isinstance(frame, p.Surface)
            ]

            if frames:
                normalised[action] = list(frames)

        return normalised

    def _get_frames(self, action):

        return self.box_animations.get(action, [])

    def _set_frame(self):

        frames = self._get_frames(
            self.current_animation
        )

        if not frames:
            return

        self.animation_index = min(
            self.animation_index,
            len(frames) - 1
        )

        self.image = frames[self.animation_index]
        self.sprite = self.image

    def _play(self, action):

        frames = self._get_frames(action)

        # If there is no break animation, remove the box safely.
        if action == "break":
            self.breaking = True

            if not frames:
                self.broken = True
                return

        # If the hit animation is missing, move to the next
        # state without getting stuck.
        if not frames:

            if action == "hit":
                next_action = self._after_hit
                self._after_hit = None

                if next_action == "break":
                    self._play("break")
                else:
                    self._play("idle")

            return

        self.current_animation = action
        self.animation_name = action
        self.animation_index = 0
        self.animation_count = 0

        self._set_frame()

    # ======================================================
    # HIT
    # ======================================================

    def hit(self):

        # A broken or currently breaking box cannot be hit again.
        if self.broken or self.breaking:
            return False

        # Prevent a single continuous collision from registering
        # repeated hits while the hit animation is playing.
        if self.current_animation == "hit":
            return False

        self.hit_count += 1

        if self.hit_count >= self.hits_to_break:
            self._after_hit = "break"
        else:
            self._after_hit = "idle"

        if self._get_frames("hit"):
            self._play("hit")

        elif self._after_hit == "break":
            self._play("break")

        else:
            self._play("idle")

        return True

    # ======================================================
    # STATE
    # ======================================================

    @property
    def is_solid(self):

        # The box stops blocking the player once it starts breaking.
        return not self.breaking and not self.broken

    # ======================================================
    # UPDATE
    # ======================================================

    def loop(self):

        # Return True when the box is ready to be removed.
        if self.broken:
            return True

        frames = self._get_frames(
            self.current_animation
        )

        if not frames:
            return False

        # Keep idle animations running if they contain multiple frames.
        self.animation_count += 1

        if self.animation_count < self.ANIMATION_DELAY:
            return False

        self.animation_count = 0

        if self.animation_index < len(frames) - 1:
            self.animation_index += 1
            self._set_frame()
            return False

        # The current non-idle animation has reached its final frame.
        if self.current_animation == "hit":

            next_action = self._after_hit
            self._after_hit = None

            if next_action == "break":
                self._play("break")

                # Handles a missing break animation.
                return self.broken

            self._play("idle")
            return False

        if self.current_animation == "break":

            self.broken = True
            return True

        # Loop idle animations.
        self.animation_index = 0
        self._set_frame()

        return False

    # ======================================================
    # DRAW
    # ======================================================

    def draw(self, screen, offset_x):

        if self.broken:
            return

        screen.blit(
            self.image,
            (
                int(self.rect.x - offset_x),
                int(self.rect.y)
            )
        )
