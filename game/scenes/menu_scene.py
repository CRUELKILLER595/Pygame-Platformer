import os
import sys

import pygame as p

from .base_scene import Scene
from ui.button import Button
from ..systems.background import TiledBackground
from ..systems.audio_manager import audio_manager


class MenuScene(Scene):

    def __init__(self, scene_manager):

        self.scene_manager = scene_manager

        # ------------------------------------------
        # FONTS
        # ------------------------------------------

        self.font = p.font.SysFont("Arial", 30)
        self.title_font = p.font.SysFont("Arial", 60)
        self.notice_font = p.font.SysFont("Arial", 18)

        # ------------------------------------------
        # BACKGROUND
        # ------------------------------------------

        # Load once instead of loading during every draw.
        self.background = TiledBackground(
            "assets/Background/Gray.png"
        )

        # ------------------------------------------
        # BUTTON ASSETS
        # ------------------------------------------

        menu_path = os.path.join(
            "assets",
            "Menu",
            "Buttons",
            "split_buttons",
        )

        main_path = os.path.join(
            "assets",
            "Menu",
            "Buttons",
        )

        play_image = p.image.load(
            os.path.join(menu_path, "Play.png")
        ).convert_alpha()

        quit_image = p.image.load(
            os.path.join(main_path, "Close.png")
        ).convert_alpha()

        # ------------------------------------------
        # BUTTONS
        # ------------------------------------------

        self.play_button = Button(
            "Play",
            (500, 300),
            (250, 70),
            self.font,
            self.start_game,
            play_image,
        )

        self.about_button = Button(
            "ABOUT",
            (500, 450),
            (250, 70),
            self.font,
            self.start_about,
            None,
        )

        self.quit_button = Button(
            "Quit",
            (500, 525),
            (250, 70),
            self.font,
            self.quit_game,
            quit_image,
        )

        self.auth_button = Button(
            "LOGIN / SIGN UP",
            (900, 525),
            (260, 70),
            self.font,
            self.open_auth,
            None,
        )

        # ------------------------------------------
        # AUTHENTICATION
        # ------------------------------------------

        self.auth_popup = None
        self.auth_notice = ""

        # Browser authentication will be integrated
        # through browser-compatible asynchronous requests.
        if sys.platform != "emscripten":

            try:
                from ui.auth import AuthPopup

                self.auth_popup = AuthPopup()

            except ImportError as error:

                print(
                    "Authentication module unavailable:",
                    error,
                )

        # ------------------------------------------
        # MUSIC
        # ------------------------------------------

        audio_manager.play_music("menu")

    # ==========================================
    # MENU ACTIONS
    # ==========================================

    def start_game(self):

        print("PLAY CLICKED")

        # Import the next scene only when requested.
        from .character_select_scene import CharacterSelectScene

        self.scene_manager.change_scene(
            CharacterSelectScene(self.scene_manager)
        )

    def open_auth(self):

        if self.auth_popup is None:

            self.auth_notice = (
                "Browser authentication is not available yet."
            )

            print(self.auth_notice)

            return

        self.auth_popup.show()

    def quit_game(self):

        audio_manager.stop_music()

        self.scene_manager.request_quit()

    def start_about(self):

        print("ABOUT BUTTON PRESSED")

        from .AboutScene import AboutScene

        self.scene_manager.change_scene(
            AboutScene(self.scene_manager)
        )

    # ==========================================
    # EVENTS
    # ==========================================

    def handle_events(self, events):

     for event in events:

        # Application shutdown.
        if event.type == p.QUIT:

            audio_manager.stop_music()
            self.scene_manager.request_quit()

            return

        # Authentication popup gets exclusive input.
        if (
            self.auth_popup is not None
            and self.auth_popup.visible
        ):

            self.auth_popup.handle_event(event)
            continue

        # Temporary browser input diagnostic.
        if event.type == p.MOUSEBUTTONDOWN:

            print(
                "[MENU CLICK]",
                "position:", event.pos,
                "button:", event.button,
                "play hit:",
                self.play_button.rect.collidepoint(event.pos),
            )

        # Forward each event to the buttons.
        self.play_button.handle_event(event)
        self.about_button.handle_event(event)
        self.quit_button.handle_event(event)
        self.auth_button.handle_event(event)

    def update(self):

        pass

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self, screen):

        # Reuse the previously loaded background.
        self.background.draw(screen)

        title = self.title_font.render(
            "PIXELBOUND",
            True,
            (0, 0, 255),
        )

        title_rect = title.get_rect(
            center=(625, 150)
        )

        screen.blit(
            title,
            title_rect,
        )

        self.play_button.draw(screen)
        self.quit_button.draw(screen)
        self.about_button.draw(screen)
        self.auth_button.draw(screen)

        if self.auth_popup is not None:

            self.auth_popup.draw(screen)

        elif self.auth_notice:

            notice = self.notice_font.render(
                self.auth_notice,
                True,
                (255, 220, 150),
            )

            screen.blit(
                notice,
                notice.get_rect(
                    center=(1030, 620)
                ),
            )