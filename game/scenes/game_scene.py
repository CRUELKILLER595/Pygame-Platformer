import pygame as p

from .base_scene import Scene

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

from .pausescene import PauseScene

from ..systems.level_manager import LevelManager
from ..systems.checkpointmanager import CheckpointManager
from ..systems.background import TiledBackground
from ..systems.audio_manager import audio_manager

from ui.button import Button


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

        self.scene_manager = scene_manager
        self.level_path = level_path

        font = p.font.SysFont(
            "Arial",
            22
        )

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

        self.level_manager = LevelManager()

        self.background = TiledBackground(
            BACKGROUND_PATH
        )

        self.offset_x = 0
        self.scroll_area_width = 200

        self.player, self.objects = (
            self.level_manager.load_level(
                self.level_path
            )
        )

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

        # If a Start object exists,
        # use it as the initial respawn position.
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

        print(
            "Loaded:",
            self.level_path
        )

        print(
            "Objects:",
            len(self.objects)
        )

        audio_manager.play_music(
            MUSIC_PATH
        )

    def draw(
        self,
        screen
    ):

        self.background.draw(
            screen
        )

        for obj in self.objects:

            obj.draw(
                screen,
                self.offset_x
            )

        if self.player is not None:

            self.player.draw(
                screen,
                self.offset_x
            )

        self.pause_button.draw(
            screen
        )

        self.options_button.draw(
            screen
        )

    def handle_move(self):

        keys = p.key.get_pressed()

        if keys[p.K_a]:

            self.player.move_left(
                PLAYER_VEL
            )

        elif keys[p.K_d]:

            self.player.move_right(
                PLAYER_VEL
            )

        else:

            self.player.x_vel = 0
            self.player.animation_count = 0

    def handle_vertical_collision(self):

        for obj in self.objects:

            if isinstance(
                obj,
                (
                    Fire,
                    Checkpoint,
                    Start,
                    End
                )
            ):
                continue

            if self.player.rect.colliderect(
                obj.rect
            ):

                if self.player.y_vel > 0:

                    self.player.rect.bottom = (
                        obj.rect.top
                    )

                    self.player.landed()

                elif self.player.y_vel < 0:

                    self.player.rect.top = (
                        obj.rect.bottom
                    )

                    self.player.hit_head()

    def handle_checkpoints(self):

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

    def handle_hazards(self):

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

    def handle_end(self):

        for obj in self.objects:

            if isinstance(
                obj,
                End
            ):

                if self.player.rect.colliderect(
                    obj.rect
                ):

                    if not obj.completed:

                        obj.complete()

                        print(
                            "LEVEL COMPLETE"
                        )

    def handle_fall(self):

        if (
            self.player.rect.top >
            HEIGHT + 200
        ):

            self.respawn_player()

    def respawn_player(self):

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

    def handle_events(
        self,
        events
    ):

        for event in events:

            if event.type == p.QUIT:

                p.quit()
                raise SystemExit

            self.pause_button.handle_event(
                event
            )

            self.options_button.handle_event(
                event
            )

            if event.type == p.KEYDOWN:

                if event.key == p.K_ESCAPE:

                    self.open_settings()

                elif event.key == p.K_SPACE:

                    if self.player.jump_count < 2:

                        self.player.jump()

    def open_settings(self):

        from .settingscene import SettingsScene

        self.scene_manager.change_scene(
            SettingsScene(
                self.scene_manager,
                self
            )
        )

    def pause_game(self):

        audio_manager.stop_music()

        self.scene_manager.change_scene(
            PauseScene(
                self.scene_manager,
                self
            )
        )

    def update(self):

        if self.player is None:
            return

        self.handle_move()

        self.player.loop(
            FPS
        )

        self.handle_vertical_collision()

        self.handle_checkpoints()

        self.handle_hazards()

        self.handle_end()

        self.handle_fall()

        # Update animated objects.
        for obj in self.objects:

            if isinstance(
                obj,
                Fire
            ):

                obj.loop()

        # Camera movement.
        if (
            self.player.rect.right -
            self.offset_x >=
            WIDTH -
            self.scroll_area_width
            and
            self.player.x_vel > 0
        ):

            self.offset_x += (
                self.player.x_vel
            )

        elif (
            self.player.rect.left -
            self.offset_x <=
            self.scroll_area_width
            and
            self.player.x_vel < 0
        ):

            self.offset_x += (
                self.player.x_vel
            )