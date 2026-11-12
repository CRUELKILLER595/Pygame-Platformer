
"""Independent level selection screen for PixelBound Editor."""

import re
from pathlib import Path

import pygame as p

from editor.scenes.base_scene import EditorBaseScene

from pixelbound_core.ui.button import Button
from pixelbound_core.graphics.tiled_background import TiledBackground

from pixelbound_core.config.paths import (
    ASSETS_DIR,
    LEVELS_DIR,
)

from editor.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class EditorLevelSelectScene(EditorBaseScene):

    LEVELS_PER_PAGE = 10
    COLUMNS = 5

    BUTTON_WIDTH = 160
    BUTTON_HEIGHT = 80

    def __init__(self, application):

        self.application = application
        self.scene_manager = application.scene_manager

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        self.current_page = 0
        self.level_files = []
        self.buttons = []

        self.selected_level_path = None

        # ------------------------------------------
        # BACKGROUND
        # ------------------------------------------

        self.background = TiledBackground(
            ASSETS_DIR / "Background" / "Gray.png"
        )

        # ------------------------------------------
        # ASSET DIRECTORIES
        # ------------------------------------------

        self.level_image_dir = (
            ASSETS_DIR / "Menu" / "Levels"
        )

        self.button_image_dir = (
            ASSETS_DIR / "Menu" / "Buttons"
        )

        # ------------------------------------------
        # FONTS
        # ------------------------------------------

        self.font = p.font.SysFont(
            "TimesNewRoman",
            28,
        )

        self.title_font = p.font.SysFont(
            "TimesNewRoman",
            55,
        )

        self.page_font = p.font.SysFont(
            "Arial",
            22,
        )

        self.status_font = p.font.SysFont(
            "Arial",
            18,
        )

        # ------------------------------------------
        # THUMBNAILS
        # ------------------------------------------

        self.level_images = self.load_level_images()

        # ------------------------------------------
        # NAVIGATION BUTTONS
        # ------------------------------------------

        self.next_image = self.load_nav_image(
            "Next.png"
        )

        self.previous_image = self.load_nav_image(
            "Previous.png"
        )

        self.previous_button = Button(
            "Previous",
            (60, self.height - 80),
            (120, 50),
            self.page_font,
            self.previous_page,
            self.previous_image,
        )
        self.back_button = Button(
    "BACK",
    (40, 35),
    (110, 45),
    self.page_font,
    self.return_to_title
)
        self.next_button = Button(
            "Next",
            (self.width - 180, self.height - 80),
            (120, 50),
            self.page_font,
            self.next_page,
            self.next_image,
        )

        # ------------------------------------------
        # LOAD LEVELS
        # ------------------------------------------

        self.load_levels()

    # ==========================================
    # IMAGE LOADING
    # ==========================================

    def load_level_images(self):

        images = {}

        for index in range(1, 51):

            path = self.level_image_dir / f"{index:02d}.png"

            if not path.is_file():
                continue

            try:
                images[index] = p.image.load(
                    str(path)
                ).convert_alpha()

            except p.error as error:
                print("Could not load level thumbnail:", path, error)

        return images

    def load_nav_image(self, filename):

        paths = [
            self.button_image_dir / filename,
            self.button_image_dir / "split_buttons" / filename,
        ]

        for path in paths:

            if not path.is_file():
                continue

            try:
                return p.image.load(
                    str(path)
                ).convert_alpha()

            except p.error as error:
                print("Could not load navigation image:", path, error)

        return None

    # ==========================================
    # LEVEL DISCOVERY
    # ==========================================

    @staticmethod
    def level_sort_key(level_path):

        match = re.search(
            r"\d+",
            level_path.stem,
        )

        if match:
            return (
                0,
                int(match.group()),
                level_path.name.lower(),
            )

        return (
            1,
            0,
            level_path.name.lower(),
        )

    def load_levels(self):

        if not LEVELS_DIR.is_dir():

            print(
                "ERROR: Levels directory not found:",
                LEVELS_DIR,
            )

            self.level_files = []
            return

        self.level_files = sorted(
            LEVELS_DIR.glob("*.json"),
            key=self.level_sort_key,
        )

        print(
            "EDITOR LEVELS FOUND:",
            len(self.level_files),
        )

        self.current_page = 0

        self.show_page()

    # ==========================================
    # THUMBNAIL RESOLUTION
    # ==========================================

    def get_level_thumbnail(self, level_path, global_index):

        match = re.search(
            r"\d+",
            level_path.stem,
        )

        candidate_numbers = []

        if match:
            candidate_numbers.append(
                int(match.group())
            )

        # Retain sequential fallback for legacy naming.
        candidate_numbers.append(global_index + 1)

        for number in dict.fromkeys(candidate_numbers):

            image = self.level_images.get(number)

            if image is not None:
                return image

        return None

    # ==========================================
    # PAGINATION
    # ==========================================

    def show_page(self):

        self.buttons.clear()

        start_index = (
            self.current_page * self.LEVELS_PER_PAGE
        )

        end_index = (
            start_index + self.LEVELS_PER_PAGE
        )

        page_files = self.level_files[
            start_index:end_index
        ]

        grid_width = (
            self.COLUMNS * self.BUTTON_WIDTH
            + (self.COLUMNS - 1) * 40
        )

        start_x = (
            self.width - grid_width
        ) // 2

        for index, level_path in enumerate(page_files):

            row = index // self.COLUMNS
            col = index % self.COLUMNS

            x = start_x + col * (
                self.BUTTON_WIDTH + 40
            )

            y = 240 + row * 145

            global_index = start_index + index

            thumbnail = self.get_level_thumbnail(
                level_path,
                global_index,
            )

            button = Button(
                level_path.stem.upper(),
                position=(x, y),
                size=(
                    self.BUTTON_WIDTH,
                    self.BUTTON_HEIGHT,
                ),
                font=self.font,
                callback=lambda path=level_path: (
                    self.select_level(path)
                ),
                image=thumbnail,
            )

            self.buttons.append(button)

    def next_page(self):

        max_page = max(
            0,
            (
                len(self.level_files) - 1
            ) // self.LEVELS_PER_PAGE,
        )

        if self.current_page < max_page:

            self.current_page += 1
            self.show_page()

    def previous_page(self):

        if self.current_page > 0:

            self.current_page -= 1
            self.show_page()

    # ==========================================
    # LEVEL SELECTION
    # ==========================================
    def return_to_title(self):

     from editor.scenes.title_scene import EditorTitleScene

     self.scene_manager.change_scene(
        EditorTitleScene(self.application)
    )
    def select_level(self, level_path):

      from editor.scenes.editor_scene import EditorScene

      selected_path = Path(level_path)

      self.application.selected_level_path = selected_path

      print("OPENING LEVEL:", selected_path.name)

      editor_scene = EditorScene(
        self.application,
        selected_path
    )

      self.application.scene_manager.change_scene(editor_scene)
    # ==========================================

    def handle_events(self, events):

        for event in events:

            if event.type == p.QUIT:
                self.application.quit()
                return

            if event.type == p.KEYDOWN:

                if event.key == p.K_ESCAPE:
                    self.return_to_title()
                    return

                elif event.key == p.K_LEFT:
                    self.previous_page()

                elif event.key == p.K_RIGHT:
                    self.next_page()

            for button in self.buttons:
                button.handle_event(event)

            self.previous_button.handle_event(event)
            self.next_button.handle_event(event)

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

        # ------------------------------------------
        # TITLE
        # ------------------------------------------

        title = self.title_font.render(
            "SELECT LEVEL TO EDIT",
            True,
            (0, 0, 255),
        )

        screen.blit(
            title,
            title.get_rect(
                center=(self.width // 2, 105)
            ),
        )

        # ------------------------------------------
        # EMPTY STATE
        # ------------------------------------------

        if not self.level_files:

            empty_text = self.font.render(
                "No level files found",
                True,
                (40, 40, 40),
            )

            screen.blit(
                empty_text,
                empty_text.get_rect(
                    center=(self.width // 2, 400)
                ),
            )

        # ------------------------------------------
        # LEVEL BUTTONS
        # ------------------------------------------

        for button in self.buttons:
            button.draw(screen)

        # ------------------------------------------
        # NAVIGATION
        # ------------------------------------------

        self.previous_button.draw(screen)
        self.next_button.draw(screen)

        total_pages = max(
            1,
            (
                len(self.level_files) - 1
            ) // self.LEVELS_PER_PAGE + 1,
        )

        page_text = self.page_font.render(
            f"PAGE {self.current_page + 1} / {total_pages}",
            True,
            (0, 0, 0),
        )

        screen.blit(
            page_text,
            page_text.get_rect(
                center=(self.width // 2, self.height - 45)
            ),
        )

        # ------------------------------------------
        # SELECTED LEVEL STATUS
        # ------------------------------------------

        if self.selected_level_path is not None:

            status = self.status_font.render(
                f"Selected: {self.selected_level_path.stem}",
                True,
                (20, 75, 35),
            )

            screen.blit(
                status,
                status.get_rect(
                    center=(self.width // 2, 205)
                ),
            )
