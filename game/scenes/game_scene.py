import pygame as p

from .base_scene import Scene
from ..systems.score_manager import ScoreManager
from ..systems.asset_manager import AssetManager,Asset
from ..systems.game_timer import GameTimer
from ..settings import (
    WIDTH,
    HEIGHT,
    FPS,
    PLAYER_VEL
)

from ..objects.player import Player
from ..objects.Block import Block
from ..objects.fire import Fire
from ..objects.checkpoint import Checkpoint
from ..objects.start import Start
from ..objects.end import End
from ..objects.fruit import Fruit
from ..objects.animated_object import AnimatedObject

from .pausescene import PauseScene

from ..systems.level_manager import LevelManager
from ..systems.checkpointmanager import CheckpointManager
from ..systems.background import TiledBackground
from ..systems.audio_manager import audio_manager

from ui.button import Button
from ui.hud import HUD


MUSIC_PATH = "game/Music/MUSIC.wav"

BACKGROUND_PATH = (
    "assets/Background/Green.png"
)


class GameScene(Scene):

    def __init__(
        self,
        scene_manager,
        level_path
    ):

        self.asset_manager = AssetManager()

        self.scene_manager = scene_manager

        self.score_manager = ScoreManager()

        self.level_path = level_path
        self.game_timer = GameTimer(
    120
)
        self.game_timer.start()
        self.hud = HUD(
    self.score_manager,
    self.game_timer
)

        self.asset_manager.load_all()
        self.asset_manager.load_all()

        print("ASSET CATEGORIES:", self.asset_manager.get_categories())
        print("TOTAL ASSETS:", len(self.asset_manager.assets))

        # --------------------------------------------------
        # FONT
        # --------------------------------------------------

        font = p.font.SysFont(
            "Arial",
            22
        )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

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
        # LEVEL
        # --------------------------------------------------

        self.level_manager = LevelManager(self.asset_manager)

        # --------------------------------------------------
        # BACKGROUND
        # --------------------------------------------------

        self.background = TiledBackground(
            BACKGROUND_PATH
        )

        # --------------------------------------------------
        # CAMERA
        # --------------------------------------------------

        self.offset_x = 0

        self.scroll_area_width = 200
        self.camera_x = 0
        self.level_start_x = 0
        self.camera_dead_zone = WIDTH // 3

        # --------------------------------------------------
        # LOAD LEVEL
        # --------------------------------------------------

        self.player, self.objects = (
            self.level_manager.load_level(
                self.level_path
            )
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
        # TEST FRUIT
        # --------------------------------------------------

     

        # --------------------------------------------------
        # CHECKPOINT
        # --------------------------------------------------

        if self.player is not None:

            self.checkpoint_manager = (
                CheckpointManager(
                    self.player.rect.topleft
                )
            )

        else:

            self.checkpoint_manager = (
                CheckpointManager()
            )

        # --------------------------------------------------
        # START POSITION
        # --------------------------------------------------

        if self.player is not None:

            for obj in self.objects:

                if isinstance(
                    obj,
                    Start
                ):

                    spawn = (
                        obj.get_spawn_position(
                            self.player
                        )
                    )


                    self.checkpoint_manager.set_start_position(
                        spawn
                    )
                    self.level_start_x = spawn[0]

        print(
            "Loaded:",
            self.level_path
        )

        print(
            "Objects:",
            len(self.objects)
        )

        # --------------------------------------------------
        # MUSIC
        # --------------------------------------------------

        audio_manager.play_music(
            MUSIC_PATH
        )

    # ======================================================
    # DRAW
    # ======================================================

    def draw(
        self,
        screen
    ): 
       


        self.background.draw(
            screen
        )

        # --------------------------------------------------
        # OBJECTS
        # --------------------------------------------------

        for obj in self.objects:

            obj.draw(
                screen,
                self.offset_x
            )

        # --------------------------------------------------
        # PLAYER
        # --------------------------------------------------

        if self.player is not None:

            self.player.draw(
                screen,
                self.offset_x
            )

        # --------------------------------------------------
        # UI
        # --------------------------------------------------

        self.pause_button.draw(
            screen
        )

        self.options_button.draw(
            screen
        )
        self.hud.draw(
    screen
)

    # ======================================================
    # HORIZONTAL MOVEMENT
    # ======================================================

    def handle_move(self):

        if self.player is None:

            return

        keys = p.key.get_pressed()

        # ----------------------------------------------
        # LEFT
        # ----------------------------------------------

        if keys[p.K_a or p.K_left_arrow]:

            self.player.move_left(
                PLAYER_VEL
            )

        # ----------------------------------------------
        # RIGHT
        # ----------------------------------------------

        elif keys[p.K_d or p.K_right_arrow]:

            self.player.move_right(
                PLAYER_VEL
            )

        # ----------------------------------------------
        # STOP
        # ----------------------------------------------

        else:

            self.player.x_vel = 0

            self.player.animation_count = 0
        if self.player.rect.x < self.level_start_x:
          self.player.rect.x = self.level_start_x
        

    # ======================================================
    # VERTICAL COLLISION
    # ======================================================

    def handle_vertical_collision(self):

        if self.player is None:

            return

        for obj in self.objects:

            if isinstance(
                obj,
                (
                    Fire,
                    Checkpoint,
                    Fruit,
                    Start,
                    End
                )
            ):

                continue

            if self.player.rect.colliderect(
                obj.rect
            ):

                # ------------------------------------------
                # FALLING
                # ------------------------------------------

                if self.player.y_vel > 0:

                    self.player.rect.bottom = (
                        obj.rect.top
                    )

                    self.player.landed()

                # ------------------------------------------
                # MOVING UP
                # ------------------------------------------

                elif self.player.y_vel < 0:

                    self.player.rect.top = (
                        obj.rect.bottom
                    )

                    self.player.hit_head()

    # ======================================================
    # CHECKPOINTS
    # ======================================================

    def handle_checkpoints(self):

        if self.player is None:

            return

        for obj in self.objects:

            if isinstance(
                obj,
                Checkpoint
            ):

                if self.player.rect.colliderect(
                    obj.rect
                ):

                    if not obj.active:

                        self.checkpoint_manager.activate_checkpoint(
                            obj
                        )

                        print(
                            "CHECKPOINT ACTIVATED"
                        )

    # ======================================================
    # HAZARDS
    # ======================================================

    def handle_hazards(self):

        if self.player is None:

            return

        for obj in self.objects:

            if isinstance(
                obj,
                Fire
            ):

                if self.player.rect.colliderect(
                    obj.rect
                ):

                    self.respawn_player()

                    return

    # ======================================================
    # END
    # ======================================================

    def handle_end(self):

     if self.player is None:
        return

     for obj in self.objects:

        if isinstance(
            obj,
            End
        ):

            if obj.check_collision(
                self.player
            ):

                print(
                    "LEVEL COMPLETE"
                )

                from .end_scene import EndScene

                self.scene_manager.change_scene(
                    EndScene(
                        self.scene_manager,
                        self.score_manager
                    )
                )

                return

    # ======================================================
    # FALL
    # ======================================================

    def handle_fall(self):

        if self.player is None:

            return

        if (
            self.player.rect.top >
            HEIGHT + 200
        ):

            self.respawn_player()

    # ======================================================
    # RESPAWN
    # ======================================================

    def respawn_player(self):

        if self.player is None:

            return

        x, y = (
            self.checkpoint_manager
            .get_respawn_position(
                self.player
            )
        )

        self.player.respawn(
            x,
            y
        )

        self.offset_x = 0

    # ======================================================
    # EVENTS
    # ======================================================

    def handle_events(
        self,
        events
    ):

        for event in events:

            # ----------------------------------------------
            # QUIT
            # ----------------------------------------------

            if event.type == p.QUIT:

                p.quit()

                raise SystemExit

            # ----------------------------------------------
            # BUTTONS
            # ----------------------------------------------

            self.pause_button.handle_event(
                event
            )

            self.options_button.handle_event(
                event
            )

            # ----------------------------------------------
            # KEYBOARD
            # ----------------------------------------------

            if event.type == p.KEYDOWN:

                # ------------------------------------------
                # ESCAPE
                # ------------------------------------------

                if event.key == p.K_ESCAPE:

                    self.pause_game()

                # ------------------------------------------
                # JUMP
                # ------------------------------------------

                elif event.key == p.K_SPACE:

                    if self.player is not None:

                        # Player itself enforces the
                        # maximum number of jumps.
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

        # --------------------------------------------------
        # HORIZONTAL MOVEMENT
        # --------------------------------------------------

        self.handle_move()

        # --------------------------------------------------
        # PLAYER PHYSICS
        # --------------------------------------------------

        self.player.loop(
            FPS
        )

        # --------------------------------------------------
        # COLLISION
        # --------------------------------------------------

        self.handle_vertical_collision()

        # --------------------------------------------------
        # CHECKPOINT
        # --------------------------------------------------

        self.handle_checkpoints()

        # --------------------------------------------------
        # HAZARDS
        # --------------------------------------------------

        self.handle_hazards()

        # --------------------------------------------------
        # END
        # --------------------------------------------------

        self.handle_end()

        # --------------------------------------------------
        # FALL
        # --------------------------------------------------

        self.handle_fall()

        # --------------------------------------------------
        # ANIMATED OBJECTS
        # --------------------------------------------------

        # Update animated objects.
        # Update animated objects.
        for obj in self.objects:

           if isinstance(
        obj,
        AnimatedObject
    ):

             if isinstance(
            obj,
            Fruit
        ):

                obj.check_collision(
                self.player,
                self.score_manager

            )

                finished = obj.loop()

             if (
            isinstance(obj, Fruit)
            and obj.collected
            and finished
        ):

               self.objects.remove(obj)
               break
        # --------------------------------------------------
        # CAMERA
        # --------------------------------------------------

        if (
            self.player.rect.right
            - self.offset_x
            >=
            WIDTH
            - self.scroll_area_width
            and
            self.player.x_vel > 0
        ):

            self.offset_x += (
                self.player.x_vel
            )

        elif (
            self.player.rect.left
            - self.offset_x
            <=
            self.scroll_area_width
            and
            self.player.x_vel < 0
        ):

            self.offset_x += (
                self.player.x_vel
            )