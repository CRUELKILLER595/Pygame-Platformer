import pygame as p

from .base_scene import Scene
from ui.button import Button
from ..systems.audio_manager import audio_manager


GAME_MUSIC_PATH = "game/Music/MUSIC.wav"


class PauseScene(Scene):

    def __init__(
        self,
        scene_manager,
        game_scene
    ):

        self.scene_manager = scene_manager
        self.game_scene = game_scene

        font = p.font.SysFont(
            "Arial",
            24
        )

        self.resume_button = Button(
            "Resume",
            (440, 220),
            (200, 50),
            font,
            self.resume_game
        )

        self.restart_button = Button(
            "Restart",
            (440, 280),
            (200, 50),
            font,
            self.restart_game
        )

        self.level_select = Button(
            "Level Select",
            (440, 340),
            (200, 50),
            font,
            self.level_select_game
        )

        self.option_button = Button(
            "Options",
            (440, 400),
            (200, 50),
            font,
            self.option_game
        )

        self.quit_button = Button(
            "Quit",
            (440, 460),
            (200, 50),
            font,
            self.quit_game
        )

    def resume_game(self):

        audio_manager.play_music(
            GAME_MUSIC_PATH
        )

        self.scene_manager.change_scene(
            self.game_scene
        )

    def restart_game(self):

        from .game_scene import GameScene

        self.scene_manager.change_scene(
            GameScene(
                self.scene_manager,
                self.game_scene.level_path
            )
        )

    def level_select_game(self):

        from .level_select_scene import LevelSelectScene

        self.scene_manager.change_scene(
            LevelSelectScene(
                self.scene_manager
            )
        )

    def option_game(self):

        from .settingscene import SettingsScene

        self.scene_manager.change_scene(
            SettingsScene(
                self.scene_manager,
                self
            )
        )

    def quit_game(self):

        audio_manager.stop_music()

        p.quit()
        raise SystemExit

    def handle_events(
        self,
        events
    ):

        for event in events:

            if event.type == p.QUIT:

                p.quit()
                raise SystemExit

            self.resume_button.handle_event(
                event
            )

            self.restart_button.handle_event(
                event
            )

            self.level_select.handle_event(
                event
            )

            self.option_button.handle_event(
                event
            )

            self.quit_button.handle_event(
                event
            )

            if event.type == p.KEYDOWN:

                if event.key == p.K_ESCAPE:

                    self.resume_game()

    def update(self):
        pass

    def draw(
        self,
        screen
    ):

        screen.fill(
            (20, 20, 20)
        )

        title_font = p.font.SysFont(
            "Arial",
            48
        )

        title = title_font.render(
            "PAUSED",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(640, 130)
            )
        )

        self.resume_button.draw(
            screen
        )

        self.restart_button.draw(
            screen
        )

        self.level_select.draw(
            screen
        )

        self.option_button.draw(
            screen
        )

        self.quit_button.draw(
            screen
        )