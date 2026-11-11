
"""Runtime trap object driven by the shared asset profile."""

from .hazard import Hazard
from ..settings import FPS
from ..systems.collision_profiles import make_collision_rect


class Trap(Hazard):

    def __init__(
        self,
        x,
        y,
        width,
        height,
        animations=None,
        name="Trap",
        image=None,
        collision_profile=None,
        animation_speed=None,
        asset=None,
    ):
        profile = {}

        if asset is not None:
            animations = getattr(asset, "animations", animations)
            name = getattr(asset, "name", name)
            image = getattr(asset, "image", image)
            profile = getattr(asset, "profile", {}) or {}

        collision_config = profile.get("collision", {})

        if collision_profile is None:
            collision_profile = collision_config.get("box")

        animation_config = profile.get("animation", {})

        if animation_speed is None:
            animation_speed = animation_config.get("speed", 5)

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            animations=animations,
            name=name,
            image=image,
            collision_profile=collision_profile,
            animation_speed=animation_speed,
        )

        self.asset = asset
        self.asset_id = getattr(asset, "id", None)
        self.profile = profile

        self.anchor = profile.get("anchor", "bottom_center")
        self.collision_type = collision_config.get("type", "hazard")

        # Use the profile's default animation when available.
        default_animation = animation_config.get("default")

        if default_animation:
            self.set_animation(default_animation)

        # Keep the hitbox synchronized with the asset profile.
        self.collision_rect = make_collision_rect(
            self.rect,
            self.collision_profile,
        )
        self.hitbox = self.collision_rect

        # --------------------------------------------------
        # SPIKE HEAD ANIMATION STATE
        # --------------------------------------------------

        normalized_name = (
            str(self.name).strip().lower().replace("_", " ")
        )

        self.is_spike_head = (
            self.asset_id == "spike_head"
            or normalized_name == "spike head"
        )

        self._spike_mode = None
        self._spike_action_frames_remaining = 0
        self._spike_idle_frames = 0

        # Blink approximately every two seconds.
        self._spike_blink_interval = max(1, FPS * 2)

    # --------------------------------------------------
    # SPIKE HEAD ANIMATIONS
    # --------------------------------------------------

    def _start_spike_animation(self, animation_name, mode):
        """Start an animation from its first frame."""

        frames = self.animations.get(animation_name, [])

        if not frames:
            print(
                f"WARNING: Animation '{animation_name}' "
                f"not loaded for {self.name}. "
                f"Available: {list(self.animations.keys())}"
            )
            return False

        self.set_animation(animation_name)

        # Explicitly reset the animation to its first frame.
        self.animation_index = 0
        self.animation_counter = 0
        self.image = self._current_frame()

        self._spike_mode = mode

        # Play one complete animation cycle.
        self._spike_action_frames_remaining = max(
            1,
            len(frames) * self.animation_speed,
        )

        return True

    def play_spike_hit(self, animation_name):
        """Play the appropriate directional Spike Head reaction."""

        if not self.is_spike_head:
            return False

        # Do not continually restart an animation already playing.
        if self._spike_mode == "hit":
            return True

        animation_name = str(animation_name).strip().lower()

        valid_animations = {
            "top_hit",
            "bottom_hit",
            "left_hit",
            "right_hit",
        }

        if animation_name not in valid_animations:
            return False

        if animation_name not in self.animations:
            print(
                f"WARNING: Missing '{animation_name}' animation "
                f"for {self.name}. "
                f"Available: {list(self.animations.keys())}"
            )
            return False

        self._spike_idle_frames = 0

        return self._start_spike_animation(
            animation_name,
            "hit",
        )

    # --------------------------------------------------
    # ANIMATION UPDATE
    # --------------------------------------------------

    def loop(self):
        """Update normal traps and Spike Head animations."""

        # Other traps retain the standard Hazard behavior.
        if not self.is_spike_head:
            return super().loop()

        # Start a blink periodically while idle.
        if self._spike_mode is None:
            self._spike_idle_frames += 1

            if (
                self._spike_idle_frames >= self._spike_blink_interval
                and "blink" in self.animations
            ):
                self._spike_idle_frames = 0

                self._start_spike_animation(
                    "blink",
                    "blink",
                )

        # Advance the current animation using Hazard's animation system.
        super().loop()

        # Keep hit and blink animations active for one complete cycle.
        if self._spike_mode is not None:
            self._spike_action_frames_remaining -= 1

            if self._spike_action_frames_remaining <= 0:
                self._spike_mode = None
                self._spike_action_frames_remaining = 0

                if "idle" in self.animations:
                    self.set_animation("idle")

                self._spike_idle_frames = 0

        return False


    
