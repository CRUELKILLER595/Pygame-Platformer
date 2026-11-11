import traceback
import json
from pathlib import Path
import random

import pygame as p

from .base_scene import Scene
from .pausescene import PauseScene
from ..systems.collision_profiles import (
    DEBUG_HITBOXES,
    DEFAULT_TRAP_HITBOX,
    TRAP_HITBOX_PROFILES,
    profile_for,
    make_collision_rect,
)

from ..settings import (
    WIDTH,
    HEIGHT,
    FPS,
    PLAYER_VEL,
)

from ..systems.score_manager import ScoreManager
from ..systems.asset_manager import AssetManager
from ..systems.game_timer import GameTimer
from ..systems.character_registry import DEFAULT_CHARACTER
from ..systems.level_manager import LevelManager
from ..systems.checkpointmanager import CheckpointManager
from ..systems.background import TiledBackground
from ..systems.audio_manager import audio_manager

from ..objects.player import Player
from ..objects.Block import Block
from ..objects.fire import Fire
from ..objects.checkpoint import Checkpoint
from ..objects.start import Start
from ..objects.end import End
from ..objects.trap import Trap
from ..objects.fruit import Fruit
from ..objects.animated_object import AnimatedObject
from ..objects.boxes import Box
from ..objects.enemy import Enemy

from ui.button import Button
from ui.hud import HUD


MUSIC_PATH = "game/Music/MUSIC.wav"
BACKGROUND_PATH = "assets/Background/Green.png"

DEFAULT_TIMER_SECONDS = 120
MAX_TIMER_SECONDS = 3600


class GameScene(Scene):

    def __init__(
        self,
        scene_manager,
        level_path,
        level_metadata=None,
        level_catalog=None
    ):
        self.scene_manager = scene_manager
        self.level_path = str(level_path)

        self.project_root = Path(__file__).resolve().parents[2]

        # --------------------------------------------------
        # LEVEL SETTINGS
        # --------------------------------------------------

        self.level_settings = {
            "timer_seconds": DEFAULT_TIMER_SECONDS,
            "soundtrack": "",
        }

        level_file = Path(self.level_path)

        try:
            if level_file.is_file():
                with level_file.open("r", encoding="utf-8") as file:
                    level_data = json.load(file)

                if isinstance(level_data, dict):
                    self.level_settings["timer_seconds"] = (
                        level_data.get(
                            "timer_seconds",
                            DEFAULT_TIMER_SECONDS
                        )
                    )

                    self.level_settings["soundtrack"] = (
                        level_data.get("soundtrack")
                        or level_data.get("soundtracks", "")
                    )
            else:
                print("Level JSON file not found:", level_file)

        except (OSError, json.JSONDecodeError) as error:
            print("Could not load level settings:", error)

        try:
            timer_seconds = int(
                self.level_settings["timer_seconds"]
            )
        except (ValueError, TypeError):
            timer_seconds = DEFAULT_TIMER_SECONDS

        if not 1 <= timer_seconds <= MAX_TIMER_SECONDS:
            timer_seconds = DEFAULT_TIMER_SECONDS

        self.level_settings["timer_seconds"] = timer_seconds

        print("LEVEL TIMER:", timer_seconds, "seconds")

        # --------------------------------------------------
        # LEVEL METADATA
        # --------------------------------------------------

        if isinstance(level_metadata, dict):
            self.level_metadata = dict(level_metadata)
        else:
            self.level_metadata = {
                "id": level_file.stem,
                "title": level_file.stem.replace(
                    "_", " "
                ).title(),
                "source": "local",
                "filename": level_file.name,
                "playable": True,
            }

        self.level_catalog = [
            dict(level)
            for level in (level_catalog or [])
        ]

        # --------------------------------------------------
        # SCORE AND TIMER
        # --------------------------------------------------

        self.score_manager = ScoreManager()

        self.game_timer = GameTimer(timer_seconds)
        self.game_timer.start()

        self.hud = HUD(
            self.score_manager,
            self.game_timer
        )

        # --------------------------------------------------
        # ASSETS
        # --------------------------------------------------

        self.asset_manager = AssetManager()
        self.asset_manager.load_all()
        # Connect loaded fruit images to the HUD.
        fruit_assets = [
    asset
    for asset in self.asset_manager.get_by_category("COLLECTIBLES")
    if asset.object_class is Fruit
]

        self.hud.set_fruit_assets(fruit_assets)

        print(
    "HUD FRUIT ICONS:",
    list(self.hud.fruit_icons.keys())
)

        print(
            "ASSET CATEGORIES:",
            self.asset_manager.get_categories()
        )
        print(
            "TOTAL ASSETS:",
            len(self.asset_manager.assets)
        )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

        font = p.font.SysFont("Arial", 22)

        self.pause_button = Button(
            "Pause",
            (20, 20),
            (100, 40),
            font,
            self.pause_game
        )

        self.options_button = Button(
            "Options",
            (130, 20),
            (110, 40),
            font,
            self.open_settings
        )

        # --------------------------------------------------
        # LEVEL MANAGER
        # --------------------------------------------------

        self.level_manager = LevelManager(self.asset_manager)

        # --------------------------------------------------
        # BACKGROUND AND CAMERA
        # --------------------------------------------------

        self.background = TiledBackground(BACKGROUND_PATH)

        self.offset_x = 0
        self.scroll_area_width = 200
        self.camera_x = 0
        self.level_start_x = 0
        self.camera_dead_zone = WIDTH // 3

        # Store the previous player rectangle for collision checks.
        self._previous_player_rect = None

        # When a hazard/enemy hits the player, let the hit animation
        # play briefly before respawning at the checkpoint.
        self._hit_respawn_pending = False
        self._hit_animation_frames = 0
        self._hit_animation_duration = max(1, int(FPS * 0.45))
        self._hit_animation_position = None

        # --------------------------------------------------
        # LOAD LEVEL
        # --------------------------------------------------

        character_id = getattr(
            self.scene_manager,
            "selected_character_id",
            DEFAULT_CHARACTER
        )

        self.player, self.objects = self.level_manager.load_level(
            self.level_path,
            character_id
        )

        print("\n========== LEVEL OBJECTS ==========")

        for obj in self.objects:
            print(
                type(obj).__name__,
                "pos =", obj.rect.topleft,
                "size =", obj.rect.size,
                "image =", obj.image.get_size()
            )

        print("===================================")

        # --------------------------------------------------
        # CHECKPOINT
        # --------------------------------------------------

        if self.player is not None:
            self.checkpoint_manager = CheckpointManager(
                self.player.rect.topleft
            )
        else:
            self.checkpoint_manager = CheckpointManager()

        # --------------------------------------------------
        # START POSITION
        # --------------------------------------------------

        if self.player is not None:
            for obj in self.objects:
                if isinstance(obj, Start):
                    spawn = obj.get_spawn_position(self.player)

                    self.checkpoint_manager.set_start_position(
                        spawn
                    )
                    self.level_start_x = spawn[0]

        print("Loaded:", self.level_path)
        print("Objects:", len(self.objects))

        # --------------------------------------------------
        # SOUNDTRACK
        # --------------------------------------------------

        self.play_level_soundtrack()

    # ======================================================
    # SOUNDTRACK
    # ======================================================

    def play_level_soundtrack(self):

        soundtrack = self.level_settings.get("soundtrack", "")

        if soundtrack:
            soundtrack_path = Path(soundtrack)

            if not soundtrack_path.is_absolute():
                soundtrack_path = self.project_root / soundtrack_path
        else:
            soundtrack_path = self.project_root / MUSIC_PATH

        if not soundtrack_path.is_file():
            print(
                "Selected soundtrack not found:",
                soundtrack_path
            )
            soundtrack_path = self.project_root / MUSIC_PATH

        if soundtrack_path.is_file():
            print("PLAYING SOUNDTRACK:", soundtrack_path)
            audio_manager.play_music(str(soundtrack_path))
        else:
            print("No valid soundtrack found for this level.")

    # ======================================================
    # DRAW
    # ======================================================

    def draw(self, screen):

       

        self.background.draw(screen)

        for obj in self.objects:
            obj.draw(screen, self.offset_x)

        # Box hitboxes can be inspected with DEBUG_HITBOXES=True.
        # Trap and enemy classes draw their own configured hitboxes.
        if DEBUG_HITBOXES:
            for obj in self.objects:
                if not isinstance(obj, Box):
                    continue
                collision_rect = self.get_object_collision_rect(obj).copy()
                collision_rect.x -= int(self.offset_x)
                p.draw.rect(screen, (0, 255, 255), collision_rect, 2)

        if self.player is not None:
            self.player.draw(screen, self.offset_x)

        self.pause_button.draw(screen)
        self.options_button.draw(screen)
        self.hud.draw(screen)

    # ======================================================
    # HORIZONTAL MOVEMENT
    # ======================================================

    def handle_move(self):

        if self.player is None:
            return

        keys = p.key.get_pressed()

        ground_speed = getattr(
            self.player,
            "move_speed",
            PLAYER_VEL,
        )
        move_speed = (
            ground_speed * 0.7
            if getattr(self.player, "jump_count", 0) > 0
            else ground_speed
        )

        if keys[p.K_a] or keys[p.K_LEFT]:
            self.player.move_left(move_speed)

        elif keys[p.K_d] or keys[p.K_RIGHT]:
            self.player.move_right(move_speed)

        else:
            self.player.x_vel = 0
            self.player.animation_count = 0

        # Prevent movement behind the level's starting position.
        if self.player.rect.x < self.level_start_x:
            self.player.rect.x = self.level_start_x

    # ======================================================
    # VERTICAL COLLISION
    # ======================================================

    
    def handle_vertical_collision(self):
        if self.player is None:
            return

        previous_rect = getattr(
            self,
            "_previous_player_rect",
            self.player.rect.copy(),
        )

        for obj in self.objects:
            # Broken/breaking boxes no longer participate in solid collision.
            if isinstance(obj, Box) and not obj.is_solid:
                continue

            if isinstance(obj, (Fire, Checkpoint, Enemy, Fruit, Start, End)):
                continue

            # Traps are normally hazards; only profile-declared platforms are solid.
            if isinstance(obj, Trap):
                profile = self.get_asset_profile_for_object(obj)
                collision_type = profile.get("collision", {}).get("type", "hazard")
                if collision_type not in ("platform", "spring"):
                    continue

            solid_rect = self.get_object_collision_rect(obj)

            horizontal_overlap = (
                min(self.player.rect.right, solid_rect.right)
                - max(self.player.rect.left, solid_rect.left)
            )
            if horizontal_overlap < 8:
                continue

            if not self.player.rect.colliderect(solid_rect):
                continue

            # Falling: land on the configured top surface.
            if self.player.y_vel > 0:
                crossed_top = (
                    previous_rect.bottom <= solid_rect.top
                    and self.player.rect.bottom >= solid_rect.top
                )
                overlapping_from_above = (
                    previous_rect.top < solid_rect.top
                    and previous_rect.bottom > solid_rect.top
                )

                if crossed_top or overlapping_from_above:
                    self.player.rect.bottom = solid_rect.top
                    if (
                        isinstance(obj, Trap)
                        and self.get_asset_profile_for_object(obj)
                            .get("collision", {}).get("type") == "spring"
                    ):
                        # A spring pad is solid but launches the player upward.
                        strength = getattr(
                            self.player,
                            "JUMP_STRENGTH",
                            getattr(self.player, "jump_strength", 14),
                        )
                        self.player.y_vel = -abs(float(strength)) * 1.35
                        self.player.fall_count = 0
                        self.player.jump_count = 1
                        self.player.animation_count = 0
                    else:
                        self.player.landed()

            # Rising: hit the underside of a solid object.
            elif self.player.y_vel < 0:
                crossed_underside = (
                    previous_rect.top >= solid_rect.bottom
                    and self.player.rect.top <= solid_rect.bottom
                )
                if crossed_underside:
                    self.player.rect.top = solid_rect.bottom
                    self.player.hit_head()
                    if isinstance(obj, Box):
                        obj.hit()

    # ======================================================
    # CHECKPOINTS
    # ======================================================

    def handle_checkpoints(self):

        if self.player is None:
            return

        for obj in self.objects:
            if isinstance(obj, Checkpoint):
                if self.player.rect.colliderect(obj.rect):
                    if not obj.active:
                        self.checkpoint_manager.activate_checkpoint(obj)
                        print("CHECKPOINT ACTIVATED")

    # ======================================================
    # HAZARDS
    # ======================================================
    @staticmethod
    def get_asset_profile_for_object(obj):
        profile = getattr(obj, "profile", None)
        if profile:
            return profile
        asset = getattr(obj, "asset", None)
        return getattr(asset, "profile", {}) or {}

    def get_object_collision_rect(self, obj):
        """Resolve collision geometry from the object's asset profile."""
        profile = self.get_asset_profile_for_object(obj)
        collision_config = profile.get("collision", {})
        ratios = collision_config.get("box")

        if ratios:
            collision_rect = make_collision_rect(obj.rect, ratios)
            # Keep the object hitbox available for debugging/other systems.
            if hasattr(obj, "collision_rect"):
                obj.collision_rect = collision_rect
                obj.hitbox = collision_rect
            return collision_rect

        return getattr(obj, "collision_rect", obj.rect)

    def get_hazard_collision_rect(self, obj):
        profile = self.get_asset_profile_for_object(obj)
        ratios = profile.get("collision", {}).get("box")
        if ratios:
            return self.get_object_collision_rect(obj)

        # Compatibility fallback for legacy Fire objects and older assets.
        asset = getattr(obj, "asset", None)
        name = (
            getattr(obj, "name", None)
            or getattr(asset, "name", None)
            or type(obj).__name__
        )
        ratios = profile_for(
            name,
            TRAP_HITBOX_PROFILES,
            DEFAULT_TRAP_HITBOX,
        )
        return make_collision_rect(obj.rect, ratios)

    def start_player_hit(self, cause="HAZARD"):
        """Play the player's hit animation, then respawn at the checkpoint."""
        if self.player is None or self._hit_respawn_pending:
            return

        # Player.update_sprite() selects the hit animation when `hit` is True.
        make_hit = getattr(self.player, "make_hit", None)
        if callable(make_hit):
            make_hit()
        elif hasattr(self.player, "hit"):
            self.player.hit = True

        # Restart the hit animation from its first frame when supported.
        if hasattr(self.player, "hit_count"):
            self.player.hit_count = 0
        if hasattr(self.player, "animation_count"):
            self.player.animation_count = 0

        self.player.x_vel = 0
        self.player.y_vel = 0
        if hasattr(self.player, "fall_count"):
            self.player.fall_count = 0

        self._hit_animation_position = self.player.rect.topleft
        self._hit_animation_frames = self._hit_animation_duration
        self._hit_respawn_pending = True

        print("PLAYER HIT:", cause, "- playing hit animation before respawn")
   
    def get_spike_head_hit_animation(self, collision_rect):
        """Determine which side of the Spike Head the player hit."""
        previous = self._previous_player_rect

        if previous is None:
            previous = self.player.rect.copy()

        current = self.player.rect
        x_vel = getattr(self.player, "x_vel", 0)
        y_vel = getattr(self.player, "y_vel", 0)

        # Player falls onto the top of Spike Head.
        if (
            y_vel > 0
            and previous.bottom <= collision_rect.top
            and current.bottom >= collision_rect.top
        ):
            return "top_hit"

        # Player jumps into the underside.
        if (
            y_vel < 0
            and previous.top >= collision_rect.bottom
            and current.top <= collision_rect.bottom
        ):
            return "bottom_hit"

        # Player moves into its left side.
        if (
            x_vel > 0
            and previous.right <= collision_rect.left
            and current.right >= collision_rect.left
        ):
            return "left_hit"

        # Player moves into its right side.
        if (
            x_vel < 0
            and previous.left >= collision_rect.right
            and current.left <= collision_rect.right
        ):
            return "right_hit"

        # Fallback for collisions where the player was already overlapping.
        dx = current.centerx - collision_rect.centerx
        dy = current.centery - collision_rect.centery

        if abs(dx) > abs(dy):
            return "left_hit" if dx < 0 else "right_hit"

        return "top_hit" if dy < 0 else "bottom_hit"
    
    def handle_hazards(self):
        if self.player is None:
            return

        if getattr(self.player, "hazard_grace_frames", 0) > 0:
            return

        for obj in self.objects:
            if isinstance(obj, Trap):
                profile = self.get_asset_profile_for_object(obj)
                if profile.get("collision", {}).get("type", "hazard") != "hazard":
                    continue
            elif not isinstance(obj, Fire):
                continue

            hazard_rect = self.get_hazard_collision_rect(obj)
            if self.player.rect.colliderect(hazard_rect):
                print(
                    "RESPAWN CAUSE: HAZARD",
                    type(obj).__name__,
                    getattr(obj, "name", ""),
                    "Player:", self.player.rect,
                    "Hazard:", hazard_rect,
                )
                if (
                    isinstance(obj, Trap)
                    and getattr(obj, "is_spike_head", False)
                ):
                    animation_name = (
                        self.get_spike_head_hit_animation(hazard_rect)
                    )

                    obj.play_spike_hit(animation_name)

                    self.start_player_hit("SPIKE_HEAD")
                else:
                    self.start_player_hit("HAZARD")

                return

    # ======================================================
    # ENEMY COLLISIONS
    # ======================================================

    def handle_enemy_collisions(self):
        if self.player is None or self._hit_respawn_pending:
            return

        previous_rect = (
            self._previous_player_rect
            if self._previous_player_rect is not None
            else self.player.rect.copy()
        )

        # Iterate over a copy because a stomp removes the enemy from the list.
        for obj in list(self.objects):
            if not isinstance(obj, Enemy):
                continue
            if getattr(obj, "is_dying", False):
                continue

            enemy_rect = obj.rect
            enemy_hitbox = getattr(obj, "collision_rect", enemy_rect)

            # Jumping/falling onto an enemy defeats it and bounces the player.
            is_stomping = (
                self.player.y_vel > 0
                and previous_rect.bottom <= enemy_rect.top
                and self.player.rect.bottom >= enemy_rect.top
                and self.player.rect.colliderect(enemy_rect)
            )

            if is_stomping:
                self.player.rect.bottom = enemy_rect.top
                bounce_strength = getattr(
                    self.player,
                    "JUMP_STRENGTH",
                    getattr(self.player, "jump_strength", 14),
                )
                self.player.y_vel = -abs(float(bounce_strength))
                self.player.fall_count = 0
                self.player.jump_count = 1
                self.player.animation_count = 0
                enemy_id = str(
                    getattr(obj, "enemy_id", "")
                ).lower()

                is_turtle = (
                    enemy_id.startswith("enemy_turtle_")
                    or "turtle" in obj.name.lower()
                )

                if is_turtle and obj.start_death(duration_frames=FPS):
                    print(
                        "TURTLE DEFEATED:",
                        obj.name,
                        "- displaying bones for one second",
                    )
                else:
                    if obj in self.objects:
                        self.objects.remove(obj)

                return

            # A short grace period can prevent side-hit damage after a jump,
            # but does not prevent a valid stomp above.
            if getattr(self.player, "hazard_grace_frames", 0) > 0:
                continue

            if not getattr(obj, "lethal", True):
                continue

            if self.player.rect.colliderect(enemy_hitbox):
                print(
                    "PLAYER HIT BY ENEMY:",
                    obj.name,
                    "Player:", self.player.rect,
                    "Enemy:", enemy_hitbox,
                )
                self.start_player_hit("ENEMY")
                return

    # ======================================================
    # LEVEL PROGRESSION
    # ======================================================

    def handle_box_contacts(self):

        if self.player is None:
            return

        BOX_CENTER_BUFFER = 8

        for obj in list(self.objects):

            if not isinstance(obj, Box):
                continue

            if not obj.is_solid:
                continue

            box_rect = self.get_object_collision_rect(obj)

            # Player must be alongside the box vertically.
            vertical_overlap = (
                self.player.rect.top < box_rect.bottom
                and self.player.rect.bottom > box_rect.top
            )

            if not vertical_overlap:
                continue

            # Measure distance between horizontal centers.
            center_distance = abs(
                self.player.rect.centerx - box_rect.centerx
            )

            contact_limit = (
                self.player.rect.width + box_rect.width
            ) // 2 + BOX_CENTER_BUFFER

            if center_distance > contact_limit:
                continue

            # Force this side contact to count as the final hit.
            if (
                hasattr(obj, "hit_count")
                and hasattr(obj, "hits_to_break")
            ):
                obj.hit_count = max(
                    0,
                    int(obj.hits_to_break) - 1
                )

            obj.hit()


    def get_next_level_metadata(self):
        """Return the next playable catalogue entry after this level."""

        playable_levels = [
            level
            for level in self.level_catalog
            if level.get("playable", False)
        ]

        current_id = self.level_metadata.get("id")

        for index, level in enumerate(playable_levels):
            if level.get("id") == current_id:
                if index + 1 < len(playable_levels):
                    return dict(playable_levels[index + 1])
                return None

        return None

    # ======================================================
    # END / LEVEL COMPLETION
    # ======================================================

    def handle_end(self):

        if self.player is None:
            return False

        for obj in self.objects:
            if isinstance(obj, End) and obj.check_collision(self.player):
                print("LEVEL COMPLETE")

                from .end_scene import EndScene

                self.scene_manager.change_scene(
                    EndScene(
                        self.scene_manager,
                        self.score_manager,
                        current_level_metadata=self.level_metadata,
                        next_level_metadata=self.get_next_level_metadata(),
                        level_catalog=self.level_catalog
                    )
                )

                return True

        return False

    # ======================================================
    # FALL
    # ======================================================

    def handle_fall(self):

        if self.player is None:
            return

        if self.player.rect.top > HEIGHT + 200:
            print(
                "RESPAWN CAUSE: FALL",
                "Player:", self.player.rect,
                "Y velocity:", self.player.y_vel
            )
            self.respawn_player()

    # ======================================================
    # RESPAWN
    # ======================================================

    def respawn_player(self):
        if self.player is None:
            return

        print("\n=== PLAYER RESPAWN REQUESTED ===")
        print("Player position:", self.player.rect)
        print("Vertical velocity:", self.player.y_vel)
        print(
            "Jump grace frames:",
            getattr(self.player, "hazard_grace_frames", "MISSING"),
        )
        traceback.print_stack(limit=5)

        x, y = self.checkpoint_manager.get_respawn_position(self.player)
        self.player.respawn(x, y)
        self._hit_respawn_pending = False
        self._hit_animation_frames = 0
        self._hit_animation_position = None
        self.offset_x = 0
        self._previous_player_rect = self.player.rect.copy()

    # ======================================================
    # EVENTS
    # ======================================================

    def handle_events(self, events):

        for event in events:

            if event.type == p.QUIT:
                p.quit()
                raise SystemExit

            self.pause_button.handle_event(event)
            self.options_button.handle_event(event)

            if event.type == p.KEYDOWN:

                if event.key == p.K_ESCAPE:
                    self.pause_game()

                elif event.key == p.K_SPACE:
                    if self.player is not None:
                        self.player.jump()

    # ======================================================
    # SETTINGS
    # ======================================================

    def open_settings(self):

        from .settingscene import SettingsScene

        self.scene_manager.change_scene(
            SettingsScene(
                self.scene_manager,
                self
            )
        )

    # ======================================================
    # PAUSE
    # ======================================================

    def pause_game(self):

        audio_manager.stop_music()

        self.scene_manager.change_scene(
            PauseScene(
                self.scene_manager,
                self
            )
        )

    # ======================================================
    # UPDATE
    # ======================================================

    def update(self):

        self.game_timer.update()

        if self.player is None:
            return

        # Pause gameplay briefly while the hit animation plays. Continue
        # updating the player's sprite, but keep the player in place.
        if self._hit_respawn_pending:
            hit_position = self._hit_animation_position or self.player.rect.topleft
            self.player.x_vel = 0
            self.player.y_vel = 0
            if hasattr(self.player, "fall_count"):
                self.player.fall_count = 0

            # Player.loop() advances the hit animation and its frame counter.
            self.player.loop(FPS)
            self.player.rect.topleft = hit_position
            self.player.x_vel = 0
            self.player.y_vel = 0
            if hasattr(self.player, "fall_count"):
                self.player.fall_count = 0
            self._previous_player_rect = self.player.rect.copy()

            self._hit_animation_frames -= 1
            if self._hit_animation_frames <= 0:
                self.respawn_player()
            return

        # --------------------------------------------------
        # HORIZONTAL MOVEMENT
        # --------------------------------------------------

        self.handle_move()

        # --------------------------------------------------
        # PLAYER PHYSICS
        # --------------------------------------------------

        # Save the player's position BEFORE physics moves them.
        # Collision checks use this previous rectangle to determine
        # whether the player crossed a platform edge this frame.
        self._previous_player_rect = self.player.rect.copy()

        self.player.loop(FPS)
                    # Keep trap reactions animated while the player's hit
            # animation plays before respawning.
        for obj in list(self.objects):
                if isinstance(obj, Trap):
                    obj.loop()

                elif (
                    isinstance(obj, Enemy)
                    and getattr(obj, "is_dying", False)
                ):
                    if obj.loop() and obj in self.objects:
                        self.objects.remove(obj)

        # --------------------------------------------------
        # COLLISION
        # --------------------------------------------------
        self.handle_box_contacts()

        self.handle_vertical_collision()

        # --------------------------------------------------
        # CHECKPOINTS
        # --------------------------------------------------
 
        self.handle_hazards()
        if self._hit_respawn_pending:
            return

        self.handle_checkpoints()

        # --------------------------------------------------
        # HAZARDS
        # --------------------------------------------------

        

        # --------------------------------------------------
        # LEVEL COMPLETION
        # --------------------------------------------------

        if self.handle_end():
            return

        # --------------------------------------------------
        # FALL
        # --------------------------------------------------

        self.handle_fall()

        # --------------------------------------------------
        # ANIMATED OBJECTS, BOXES, AND FRUITS
        # --------------------------------------------------

        
        for obj in list(self.objects):

            # ----------------------------------------------
            # FIRE AND TRAPS
            # ----------------------------------------------

            if isinstance(obj, (Fire, Trap)):
                obj.loop()
                continue
            # ----------------------------------------------
            # ENEMIES
            # ----------------------------------------------
            if isinstance(obj, Enemy):
                finished = obj.loop()

                if finished and obj in self.objects:
                    self.objects.remove(obj)

                continue
            # ----------------------------------------------
            # BOX BREAKING AND FRUIT REWARDS
            # ----------------------------------------------

            
            if isinstance(obj, Box):

                finished = obj.loop()

                if finished:
                    print(
                        "BOX BREAK FINISHED:",
                        obj.name,
                        "Reward:",
                        getattr(obj.reward_asset, "name", None)
                    )

                    if not obj.reward_spawned:
                        reward_asset = obj.reward_asset

                        # Get a fallback reward if the box has none.
                        if reward_asset is None:
                            fruit_assets = [
                                asset
                                for asset in (
                                    self.asset_manager.get_by_category(
                                        "COLLECTIBLES"
                                    )
                                )
                                if asset.object_class is Fruit
                            ]

                            print(
                                "AVAILABLE FRUITS:",
                                [asset.name for asset in fruit_assets]
                            )

                            if fruit_assets:
                                reward_asset = random.choice(
                                    fruit_assets
                                )

                        if reward_asset is not None:
                            fruit_x = (
                                obj.rect.centerx+5
                                
                            )
                            fruit_y = (
                                obj.rect.top

                            )

                            fruit = Fruit(
                                fruit_x,
                                fruit_y,
                                reward_asset,
                                reward_asset.name
                            )
                            fruit.awaiting_separation = True

                            self.objects.append(fruit)
                            obj.reward_spawned = True

                            print(
                                "CREATING FRUIT:",
                                reward_asset.name,
                                "Position:",
                                fruit.rect
                            )
                        else:
                            print(
                                "ERROR: No fruit reward asset available."
                            )

                    if obj in self.objects:
                        self.objects.remove(obj)

                continue


            # ----------------------------------------------
            # OTHER ANIMATED OBJECTS
            # ----------------------------------------------

            if not isinstance(obj, AnimatedObject):
                continue

            if isinstance(obj, Fruit):
                # Prevent immediate collection when a reward spawns inside
                # or overlapping the player. Enable collection after separation.
                if getattr(obj, "awaiting_separation", False):
                    if not obj.rect.colliderect(self.player.rect):
                        obj.awaiting_separation = False

                if not getattr(obj, "awaiting_separation", False):
                    obj.check_collision(self.player, self.score_manager)

            finished = obj.loop()


            if (
                isinstance(obj, Fruit)
                and obj.collected
                and finished
            ):
                if obj in self.objects:
                    self.objects.remove(obj)

        # Enemies have moved and refreshed their hitboxes this frame.
        self.handle_enemy_collisions()
        if self._hit_respawn_pending:
            return

        # --------------------------------------------------
        # CAMERA
        # --------------------------------------------------

        if (
            self.player.rect.right - self.offset_x
            >= WIDTH - self.scroll_area_width
            and self.player.x_vel > 0
        ):
            self.offset_x += self.player.x_vel

        elif (
            self.player.rect.left - self.offset_x
            <= self.scroll_area_width
            and self.player.x_vel < 0
        ):
            self.offset_x += self.player.x_vel