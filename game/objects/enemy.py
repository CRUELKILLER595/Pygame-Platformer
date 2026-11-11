import pygame as p
from ..settings import FPS
from ..systems.collision_profiles import (
    DEBUG_HITBOXES,
    DEFAULT_ENEMY_HITBOX,
    ENEMY_HITBOX_PROFILES,
    make_collision_rect,
    profile_for,
)

from ..systems.enemy_registry import ENEMY_REGISTRY


class Enemy(p.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
        width,
        height,
        animations=None,
        name="Enemy",
        image=None,
        speed=None,
        patrol_distance=None,
        collision_profile=None,
        asset=None,
    ):
        super().__init__()

        # --------------------------------------------------
        # ASSET INFORMATION
        # --------------------------------------------------

        enemy_id = None

        if asset is not None:

            enemy_id = (
                getattr(asset, "enemy_id", None)
                or getattr(asset, "id", None)
            )

            animations = getattr(
                asset,
                "animations",
                animations
            )

            name = getattr(
                asset,
                "name",
                name
            )

            image = getattr(
                asset,
                "image",
                image
            )

        # --------------------------------------------------
        # ENEMY REGISTRY
        # --------------------------------------------------

        config = {}

        # Prefer an exact registry ID.
        if enemy_id in ENEMY_REGISTRY:
            config = ENEMY_REGISTRY[enemy_id]

        else:
            # Fallback: resolve using the display name.
            normalized_name = str(name or "").strip().lower()

            for registry_id, definition in ENEMY_REGISTRY.items():

                registered_name = (
                    definition.get("name", "")
                    .strip()
                    .lower()
                )

                if (
                    registry_id.lower() == normalized_name
                    or registered_name == normalized_name
                ):
                    enemy_id = registry_id
                    config = definition
                    break

        self.enemy_id = enemy_id

        self.name = config.get(
            "name",
            str(name or "Enemy")
        )

        # --------------------------------------------------
        # SIZE AND MOVEMENT
        # --------------------------------------------------

        self.width = max(1, int(width))
        self.height = max(1, int(height))

        self.speed = float(
            config.get("speed", 1.0)
            if speed is None
            else speed
        )

        self.patrol_distance = max(
            0.0,
            float(
                config.get(
                    "patrol_distance",
                    self.width * 3
                )
                if patrol_distance is None
                else patrol_distance
            )
        )

        self.lethal = bool(
            config.get(
                "lethal",
                getattr(asset, "lethal", True)
            )
        )

        self.animation_speed = max(
            1,
            int(config.get("animation_speed", 5))
        )

        # --------------------------------------------------
        # VISUAL RECTANGLE
        # --------------------------------------------------

        self.rect = p.Rect(
            int(x),
            int(y),
            self.width,
            self.height
        )

        # --------------------------------------------------
        # ANIMATIONS
        # --------------------------------------------------

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

        # Fallback if an asset provides only a static image.
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
        self.is_dying = False
        self._death_frames_remaining = 0

        # --------------------------------------------------
        # PATROL BOUNDS
        # --------------------------------------------------

        self.left_bound = float(x)

        self.right_bound = (
            float(x) + self.patrol_distance
        )

        self.world_x = float(x)

        # 1 = right, -1 = left.
        self.direction = 1

        self.image = self._current_frame()

        # --------------------------------------------------
        # COLLISION HITBOX
        # --------------------------------------------------

        self.collision_profile = (
            collision_profile
            or profile_for(
                self.name,
                ENEMY_HITBOX_PROFILES,
                DEFAULT_ENEMY_HITBOX
            )
        )

        self.collision_rect = make_collision_rect(
            self.rect,
            self.collision_profile
        )

        self.hitbox = self.collision_rect
        self.debug_hitbox = DEBUG_HITBOXES

    # ==================================================
    # INITIAL ANIMATION
    # ==================================================

    def _initial_animation(self):

        for key in (
            "walk",
            "run",
            "move",
            "idle",
            "fly",
            "flying",
            "on",
        ):
            if key in self.animations:
                return key

        return next(
            iter(self.animations),
            "idle"
        )

    # ==================================================
    # CURRENT FRAME
    # ==================================================

    def _current_frame(self):

        frames = self.animations.get(
            self.animation_name,
            []
        )

        if not frames:
            return p.Surface(
                (self.width, self.height),
                p.SRCALPHA
            )

        frame = frames[
            self.animation_index % len(frames)
        ]

        if self.direction < 0:

            return p.transform.flip(
                frame,
                True,
                False
            )

        return frame

    # ==================================================
    # UPDATE
    # ==================================================
    def start_death(self, duration_frames=None):
        """Play the death animation and keep the bones visible temporarily."""
        if self.is_dying:
            return True

        death_frames = self.animations.get("death", [])

        if not death_frames:
            return False

        self.is_dying = True
        self.lethal = False
        self.speed = 0.0
        self.patrol_distance = 0.0
        self.world_x = float(self.rect.x)

        self.animation_name = "death"
        self.animation_index = 0
        self.animation_counter = 0

        if duration_frames is None:
            duration_frames = FPS

        self._death_frames_remaining = max(
            1,
            int(duration_frames),
        )

        self.image = self._current_frame()
        return True


    def loop(self):

                # While dying, animate the bones without moving or patrolling.
        # Once the death timer expires, signal GameScene to remove us.
        if self.is_dying:
            frames = self.animations.get("death", [])

            if not frames:
                return True

            # Play the death animation once, then hold its last frame.
            if (
                len(frames) > 1
                and self.animation_index < len(frames) - 1
            ):
                self.animation_counter += 1

                if self.animation_counter >= self.animation_speed:
                    self.animation_counter = 0
                    self.animation_index += 1

            self.image = self._current_frame()

            self._death_frames_remaining -= 1

            return self._death_frames_remaining <= 0

        if (
            self.patrol_distance > 0
            and self.speed > 0
        ):

            self.world_x += (
                self.speed * self.direction
            )

            if self.world_x >= self.right_bound:

                self.world_x = self.right_bound
                self.direction = -1

            elif self.world_x <= self.left_bound:

                self.world_x = self.left_bound
                self.direction = 1

            self.rect.x = round(self.world_x)

        # ----------------------------------------------
        # ANIMATION
        # ----------------------------------------------

        frames = self.animations.get(
            self.animation_name,
            []
        )

        if len(frames) > 1:

            self.animation_counter += 1

            if (
                self.animation_counter
                >= self.animation_speed
            ):

                self.animation_counter = 0

                self.animation_index = (
                    self.animation_index + 1
                ) % len(frames)

        self.image = self._current_frame()

        # ----------------------------------------------
        # UPDATE HITBOX
        # ----------------------------------------------

        self.collision_rect = make_collision_rect(
            self.rect,
            self.collision_profile
        )

        self.hitbox = self.collision_rect

        return False

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self, win, offset_x=0):

        win.blit(
            self.image,
            (
                int(self.rect.x - offset_x),
                int(self.rect.y)
            )
        )

        if self.debug_hitbox:

            debug_rect = self.collision_rect.copy()
            debug_rect.x -= int(offset_x)

            p.draw.rect(
                win,
                (255, 0, 0),
                debug_rect,
                2
            )