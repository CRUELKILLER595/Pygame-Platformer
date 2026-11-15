import json
import os
import re
import sys

from pathlib import Path

import pygame as p

from ui.button import Button
from .base_scene import Scene

from game.settings import WIDTH, HEIGHT
from game.systems.audio_manager import audio_manager
from game.systems.background import TiledBackground


UI_PATH = os.path.join(
    "assets",
    "Menu",
    "Levels",
)

BUTTON_PATH = os.path.join(
    "assets",
    "Menu",
    "Buttons",
)


class LevelSelectScene(Scene):

    def __init__(self, scene_manager):

        self.scene_manager = scene_manager

        self.width = WIDTH
        self.height = HEIGHT

        self.current_page = 0
        self.levels_per_page = 10

        self.levels = []
        self.buttons = []

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

        # ------------------------------------------
        # BACKGROUND
        # ------------------------------------------

        self.background = TiledBackground(
            "assets/Background/Gray.png"
        )

        # ------------------------------------------
        # IMAGE CACHE
        # ------------------------------------------

        self.level_image_cache = {}

        self.next_image = self.load_nav_image(
            "Next.png"
        )

        self.previous_image = self.load_nav_image(
            "Previous.png"
        )

        # ------------------------------------------
        # NAVIGATION BUTTONS
        # ------------------------------------------

        self.next_button = Button(
            "Next",
            (WIDTH - 180, HEIGHT - 70),
            (120, 50),
            self.page_font,
            self.next_page,
            self.next_image,
        )

        self.previous_button = Button(
            "Previous",
            (60, HEIGHT - 70),
            (120, 50),
            self.page_font,
            self.previous_page,
            self.previous_image,
        )

        # Load level catalogue.
        self.load_levels()

    # ==========================================
    # IMAGE LOADING
    # ==========================================

    def load_nav_image(self, filename):

        paths = [
            os.path.join(
                BUTTON_PATH,
                filename,
            ),

            os.path.join(
                BUTTON_PATH,
                "split_buttons",
                filename,
            ),
        ]

        for path in paths:

            if os.path.exists(path):

                return p.image.load(
                    path
                ).convert_alpha()

        return None

    def load_level_image(self, index):

        # Level images are numbered 01.png to 50.png.
        image_number = (index % 50) + 1

        if image_number in self.level_image_cache:
            return self.level_image_cache[image_number]

        image_path = os.path.join(
            UI_PATH,
            f"{image_number:02d}.png",
        )

        if not os.path.exists(image_path):
            self.level_image_cache[image_number] = None
            return None

        image = p.image.load(
            image_path
        ).convert_alpha()

        self.level_image_cache[image_number] = image

        return image

    # ==========================================
    # LEVEL SORTING
    # ==========================================

    @staticmethod
    def level_sort_key(identifier):

        match = re.search(
            r"\d+",
            str(identifier),
        )

        if match:

            return (
                0,
                int(match.group()),
                str(identifier).lower(),
            )

        return (
            1,
            0,
            str(identifier).lower(),
        )

    # ==========================================
    # LOCAL LEVEL LOADING
    # ==========================================

    def load_local_levels(self):

        levels = []

        levels_directory = Path("levels")

        if not levels_directory.is_dir():

            print("Levels directory not found.")

            return levels

        for path in levels_directory.glob("*.json"):

            try:

                with path.open(
                    "r",
                    encoding="utf-8",
                ) as file:

                    level_data = json.load(file)

                if not isinstance(level_data, dict):
                    continue

            except (
                json.JSONDecodeError,
                OSError,
                UnicodeDecodeError,
            ):

                print("Skipping invalid level:", path)
                continue

            levels.append({
                "id": path.stem,
                "title": path.stem.replace(
                    "_",
                    " ",
                ).title(),
                "playable": True,
                "status": "local",
                "parse_status": "valid",
                "source": "local",
                "filename": path.name,
            })

        return levels

    # ==========================================
    # LEVEL CATALOGUE
    # ==========================================

    def load_levels(self):

        self.buttons.clear()

        levels = []

        # Standard browser build:
        # use local JSON files and avoid synchronous
        # requests-based networking.
        if sys.platform != "emscripten":

            try:

                from game.systems.online_client import (
                    fetch_level_catalog,
                )

                levels = fetch_level_catalog()

                for level in levels:
                    level["source"] = "online"

                print(
                    f"Loaded {len(levels)} online levels."
                )

            except Exception as error:

                print(
                    "Online catalogue unavailable:",
                    error,
                )

        # Use local levels when running in the browser,
        # or when the desktop online catalogue is unavailable.
        if not levels:

            print("Loading local levels.")

            levels = self.load_local_levels()

        self.levels = sorted(
            levels,
            key=lambda level: self.level_sort_key(
                level.get(
                    "id",
                    level.get("title", ""),
                )
            ),
        )

        self.current_page = 0

        self.show_page()

        print(
            f"Level catalogue ready: {len(self.levels)} entries."
        )

    # ==========================================
    # PAGE GENERATION
    # ==========================================

    def show_page(self):

        self.buttons.clear()

        start = (
            self.current_page
            * self.levels_per_page
        )

        page_levels = self.levels[
            start:start + self.levels_per_page
        ]

        cell_width = WIDTH // 5

        button_width = min(
            180,
            cell_width - 20,
        )

        button_height = 85

        for i, level in enumerate(page_levels):

            title = level.get(
                "title",
                level.get("id", "LEVEL"),
            ).upper()

            if not level.get("playable", False):
                title += " *"

            row = i // 5
            col = i % 5

            x = (
                col * cell_width
                + (cell_width - button_width) // 2
            )

            y = (
                HEIGHT // 3
                + row * 130
            )

            global_index = start + i

            image = self.load_level_image(
                global_index
            )

            self.buttons.append(
                Button(
                    title,
                    position=(x, y),
                    size=(button_width, button_height),
                    font=self.font,
                    callback=lambda selected=level: (
                        self.start_level(selected)
                    ),
                    image=image,
                )
            )

    # ==========================================
    # PAGE NAVIGATION
    # ==========================================

    def next_page(self):

        max_page = max(
            0,
            (len(self.levels) - 1)
            // self.levels_per_page,
        )

        if self.current_page < max_page:

            self.current_page += 1

            self.show_page()

    def previous_page(self):

        if self.current_page > 0:

            self.current_page -= 1

            self.show_page()

    # ==========================================
    # NEXT PLAYABLE LEVEL
    # ==========================================

    def get_next_playable_level(self, current_level_id):

        playable_levels = [
            level
            for level in self.levels
            if level.get("playable", False)
        ]

        playable_levels.sort(
            key=lambda level: self.level_sort_key(
                level.get("id", "")
            )
        )

        for index, level in enumerate(playable_levels):

            if level.get("id") == current_level_id:

                if index + 1 < len(playable_levels):

                    return dict(
                        playable_levels[index + 1]
                    )

                return None

        return None

    # ==========================================
    # START LEVEL
    # ==========================================

    def start_level(self, level):

        if not level.get("playable", False):

            print(
                f"{level.get('title', 'Level')} "
                "needs repair before it can be played."
            )

            return

        try:

            if level.get("source") == "online":

                if sys.platform == "emscripten":

                    raise RuntimeError(
                        "Online levels are not enabled in browser mode."
                    )

                from game.systems.online_client import (
                    download_level_to_cache,
                )

                level_path = download_level_to_cache(
                    level["id"]
                )

            else:

                level_path = str(
                    Path("levels") / level["filename"]
                )

            if not Path(level_path).is_file():

                raise FileNotFoundError(
                    f"Level file not found: {level_path}"
                )

        except Exception as error:

            print(
                "Could not load level:",
                error,
            )

            return

        # Import gameplay only when a level is selected.
        from .game_scene import GameScene

        game_scene = GameScene(
            self.scene_manager,
            level_path,
            level_metadata=dict(level),
            level_catalog=self.levels,
        )

        # GameScene starts its own soundtrack through
        # the shared AudioManager.
        self.scene_manager.change_scene(
            game_scene
        )

        print(
            "Started level:",
            level.get("id"),
        )

    # ==========================================
    # EVENTS
    # ==========================================

    def handle_events(self, events):

        for event in events:

            if event.type == p.QUIT:

                self.scene_manager.request_quit()
                return

            if (
                event.type == p.KEYDOWN
                and event.key == p.K_ESCAPE
            ):

                from .menu_scene import MenuScene

                self.scene_manager.change_scene(
                    MenuScene(self.scene_manager)
                )

                return

            for button in self.buttons:
                button.handle_event(event)

            self.next_button.handle_event(event)
            self.previous_button.handle_event(event)

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self):

        pass

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self, screen):

        # Reuse cached background.
        self.background.draw(screen)

        title = self.title_font.render(
            "LEVEL SELECT",
            True,
            (0, 255, 0),
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    100,
                )
            ),
        )

        total_pages = max(
            1,
            (
                len(self.levels)
                + self.levels_per_page - 1
            ) // self.levels_per_page,
        )

        page_text = self.page_font.render(
            f"PAGE {self.current_page + 1} / {total_pages}",
            True,
            (255, 255, 255),
        )

        screen.blit(
            page_text,
            page_text.get_rect(
                center=(
                    self.width // 2,
                    self.height - 45,
                )
            ),
        )

        for button in self.buttons:
            button.draw(screen)

        self.next_button.draw(screen)
        self.previous_button.draw(screen)