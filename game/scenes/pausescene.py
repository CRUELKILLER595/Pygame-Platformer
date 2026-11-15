import pygame as p

from .base_scene import Scene
from ui.button import Button
from ..systems.audio_manager import audio_manager
from ..systems.background import TiledBackground


class PauseScene(Scene):

    def __init__(self, scene_manager, game_scene):

        self.scene_manager = scene_manager
        self.game_scene = game_scene

        # ------------------------------------------
        # BACKGROUND
        # ------------------------------------------

        self.background = TiledBackground(
            "assets/Background/Blue.png"
        )

        # ------------------------------------------
        # FONTS
        # ------------------------------------------

        self.font = p.font.SysFont(
            "Times New Roman",
            24
        )

        self.title_font = p.font.SysFont(
            "Arial",
            48
        )

        # ------------------------------------------
        # BUTTONS
        # ------------------------------------------

        self.resume_button = Button(
            "Resume",
            (440, 210),
            (200, 50),
            self.font,
            self.resume_game
        )

        self.restart_button = Button(
            "Restart",
            (440, 280),
            (200, 50),
            self.font,
            self.restart_game
        )

        self.menu_button = Button(
            "Main Menu",
            (440, 350),
            (200, 50),
            self.font,
            self.main_menu
        )

        self.level_select = Button(
            "Level Select",
            (440, 420),
            (200, 50),
            self.font,
            self.level_select_game
        )

        self.option_button = Button(
            "Options",
            (440, 490),
            (200, 50),
            self.font,
            self.option_game
        )

        self.quit_button = Button(
            "Quit",
            (440, 560),
            (200, 50),
            self.font,
            self.quit_game
        )

    # ==========================================
    # RESUME
    # ==========================================

    def resume_game(self):

        # Resume the existing timer.
        self.game_scene.game_timer.resume()

        # Continue the existing music stream.
        audio_manager.resume_music()

        # Return to the same GameScene instance.
        self.scene_manager.change_scene(
            self.game_scene
        )

    # ==========================================
    # RESTART
    # ==========================================

    def restart_game(self):

        from .game_scene import GameScene

        # Stop the old soundtrack.
        # The new GameScene will load its soundtrack.
        audio_manager.stop_music()

        restarted_scene = GameScene(
            self.scene_manager,
            self.game_scene.level_path,
            level_metadata=self.game_scene.level_metadata,
            level_catalog=self.game_scene.level_catalog,
        )

        self.scene_manager.change_scene(
            restarted_scene
        )

    # ==========================================
    # MAIN MENU
    # ==========================================

    def main_menu(self):

        from .menu_scene import MenuScene

        audio_manager.play_music("menu")

        self.scene_manager.change_scene(
            MenuScene(self.scene_manager)
        )

    # ==========================================
    # LEVEL SELECT
    # ==========================================

    def level_select_game(self):

        from .level_select_scene import LevelSelectScene

        audio_manager.play_music("menu")

        self.scene_manager.change_scene(
            LevelSelectScene(self.scene_manager)
        )

    # ==========================================
    # OPTIONS
    # ==========================================

    def option_game(self):

        from .settingscene import SettingsScene

        self.scene_manager.change_scene(
            SettingsScene(
                self.scene_manager,
                self
            )
        )

    # ==========================================
    # QUIT
    # ==========================================

    def quit_game(self):

        audio_manager.stop_music()

        self.scene_manager.request_quit()

    # ==========================================
    # EVENTS
    # ==========================================

    def handle_events(self, events):

        for event in events:

            if event.type == p.QUIT:

                audio_manager.stop_music()

                self.scene_manager.request_quit()

                return

            self.resume_button.handle_event(event)

            self.restart_button.handle_event(event)

            self.menu_button.handle_event(event)

            self.level_select.handle_event(event)

            self.option_button.handle_event(event)

            self.quit_button.handle_event(event)

            if event.type == p.KEYDOWN:

                if event.key == p.K_ESCAPE:
                    self.resume_game()
                    return

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self):

        pass

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self, screen):

        self.background.draw(screen)

        title = self.title_font.render(
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

        self.resume_button.draw(screen)

        self.menu_button.draw(screen)

        self.restart_button.draw(screen)

        self.level_select.draw(screen)

        self.option_button.draw(screen)

        self.quit_button.draw(screen)