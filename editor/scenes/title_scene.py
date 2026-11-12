
"""Standalone title screen for the PixelBound Editor."""

import pygame as p

from editor.config import WINDOW_WIDTH, WINDOW_HEIGHT
from editor.scenes.base_scene import EditorBaseScene

from pixelbound_core.config.paths import ASSETS_DIR
from pixelbound_core.graphics.tiled_background import TiledBackground
from pixelbound_core.ui.button import Button


class EditorTitleScene(EditorBaseScene):

    def __init__(self, application):

        self.application = application
        self.scene_manager = application.scene_manager

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        # Background
        self.background = TiledBackground(
            ASSETS_DIR / "Background" / "Gray.png"
        )

        # Fonts
        self.title_font = p.font.SysFont(
            "Arial", 82, bold=True
        )

        self.heading_font = p.font.SysFont(
            "Arial", 42, bold=True
        )

        self.subtitle_font = p.font.SysFont(
            "Arial", 23
        )

        self.button_font = p.font.SysFont(
            "Arial", 24, bold=True
        )

        self.footer_font = p.font.SysFont(
            "Arial", 16
        )

        # Main panel
        self.panel_rect = p.Rect(
            self.width // 2 - 430,
            145,
            860,
            650
        )

        # Buttons
        button_width = 380
        button_x = (self.width - button_width) // 2

        self.open_button = Button(
            "OPEN LEVEL SELECTOR",
            position=(button_x, 515),
            size=(button_width, 68),
            font=self.button_font,
            callback=self.open_level_selector
        )

        self.quit_button = Button(
            "QUIT EDITOR",
            position=(button_x, 605),
            size=(button_width, 60),
            font=self.button_font,
            callback=self.application.quit
        )

    # ------------------------------------------
    # NAVIGATION
    # ------------------------------------------

    def open_level_selector(self):

        # Local import prevents circular dependencies.
        from editor.scenes.level_select_scene import (
            EditorLevelSelectScene
        )

        self.scene_manager.change_scene(
            EditorLevelSelectScene(self.application)
        )

    # ------------------------------------------
    # EVENTS
    # ------------------------------------------

    def handle_events(self, events):

        for event in events:

            if event.type == p.QUIT:
                self.application.quit()
                return

            if event.type == p.KEYDOWN:

                if event.key == p.K_ESCAPE:
                    self.application.quit()
                    return

                if event.key in (p.K_RETURN, p.K_SPACE):
                    self.open_level_selector()
                    return

            self.open_button.handle_event(event)
            self.quit_button.handle_event(event)

    def update(self):
        pass

    # ------------------------------------------
    # BUTTON RENDERING
    # ------------------------------------------

    @staticmethod
    def draw_button(screen, button):

        hovered = button.rect.collidepoint(
            p.mouse.get_pos()
        )

        fill = (
            (65, 95, 125)
            if hovered
            else (42, 57, 78)
        )

        border = (
            (170, 205, 235)
            if hovered
            else (105, 135, 170)
        )

        p.draw.rect(
            screen,
            fill,
            button.rect,
            border_radius=10
        )

        p.draw.rect(
            screen,
            border,
            button.rect,
            width=2,
            border_radius=10
        )

        label = button.font.render(
            button.text,
            True,
            (245, 248, 255)
        )

        screen.blit(
            label,
            label.get_rect(
                center=button.rect.center
            )
        )

    # ------------------------------------------
    # RENDERING
    # ------------------------------------------

    def draw(self, screen):

        self.background.draw(screen)

        # Background overlay
        overlay = p.Surface(
            (self.width, self.height),
            p.SRCALPHA
        )

        overlay.fill((12, 18, 29, 175))
        screen.blit(overlay, (0, 0))

        # Main panel
        p.draw.rect(
            screen,
            (25, 34, 49),
            self.panel_rect,
            border_radius=22
        )

        p.draw.rect(
            screen,
            (103, 137, 174),
            self.panel_rect,
            width=3,
            border_radius=22
        )

        # PixelBound title
        title = self.title_font.render(
            "PIXELBOUND",
            True,
            (238, 244, 255)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(self.width // 2, 285)
            )
        )

        # Editor heading
        heading = self.heading_font.render(
            "EDITOR",
            True,
            (116, 190, 235)
        )

        screen.blit(
            heading,
            heading.get_rect(
                center=(self.width // 2, 365)
            )
        )

        # Divider
        p.draw.line(
            screen,
            (103, 137, 174),
            (self.width // 2 - 190, 410),
            (self.width // 2 + 190, 410),
            2
        )

        # Subtitle
        subtitle = self.subtitle_font.render(
            "A standalone workspace for building your worlds",
            True,
            (210, 220, 235)
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(self.width // 2, 455)
            )
        )

        # Buttons
        self.draw_button(screen, self.open_button)
        self.draw_button(screen, self.quit_button)

        # Footer
        footer = self.footer_font.render(
            "CREATE  •  EDIT  •  SAVE",
            True,
            (160, 177, 198)
        )

        screen.blit(
            footer,
            footer.get_rect(
                center=(self.width // 2, 730)
            )
        )
