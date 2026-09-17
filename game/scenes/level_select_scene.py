import pygame as p
import os
import re

from ui.button import Button
from .base_scene import Scene

from game.settings import WIDTH, HEIGHT


UI_PATH = os.path.join(
    "assets",
    "Menu",
    "Levels"
)

BUTTON_PATH = os.path.join(
    "assets",
    "Menu",
    "Buttons"
)


class LevelSelectScene(Scene):

    def __init__(
        self,
        scene_manager
    ):

        self.scene_manager = scene_manager

        self.width = WIDTH
        self.height = HEIGHT

        self.current_page = 0
        self.levels_per_page = 10
        self.level_files = []

        self.font = p.font.SysFont(
            "TimesNewRoman",
            28
        )

        self.title_font = p.font.SysFont(
            "TimesNewRoman",
            55
        )

        self.page_font = p.font.SysFont(
            "Arial",
            22
        )

        self.buttons = []

        self.level_images = []

        for i in range(1, 51):

            path = os.path.join(
                UI_PATH,
                f"{i:02d}.png"
            )

            if os.path.exists(path):

                image = p.image.load(
                    path
                ).convert_alpha()

                self.level_images.append(
                    image
                )

        self.next_image = self.load_nav_image(
            "Next.png"
        )

        self.previous_image = (
            self.load_nav_image(
                "Previous.png"
            )
        )

        self.next_button = Button(
            "Next",
            (
                WIDTH - 180,
                HEIGHT - 70
            ),
            (120, 50),
            self.page_font,
            self.next_page,
            self.next_image
        )

        self.previous_button = Button(
            "Previous",
            (
                60,
                HEIGHT - 70
            ),
            (120, 50),
            self.page_font,
            self.previous_page,
            self.previous_image
        )

        self.load_levels()

    def load_nav_image(
        self,
        filename
    ):

        paths = [
            os.path.join(
                BUTTON_PATH,
                filename
            ),
            os.path.join(
                BUTTON_PATH,
                "split_buttons",
                filename
            )
        ]

        for path in paths:

            if os.path.exists(path):

                return p.image.load(
                    path
                ).convert_alpha()

        return None

    def level_sort_key(
        self,
        filename
    ):

        match = re.search(
            r"\d+",
            filename
        )

        if match:
            return int(
                match.group()
            )

        return 9999

    def load_levels(self):

        if not os.path.exists(
            "levels"
        ):

            print(
                "ERROR: levels directory not found!"
            )

            return

        self.level_files = [
            file
            for file in os.listdir(
                "levels"
            )
            if file.endswith(".json")
        ]

        self.level_files.sort(
            key=self.level_sort_key
        )

        self.show_page()

    def show_page(self):

        self.buttons.clear()

        start_index = (
            self.current_page *
            self.levels_per_page
        )

        end_index = (
            start_index +
            self.levels_per_page
        )

        page_files = self.level_files[
            start_index:end_index
        ]

        for i, level_file in enumerate(
            page_files
        ):

            row = i // 5
            col = i % 5

            x = 140 + col * 220
            y = 220 + row * 130

            global_index = (
                start_index + i
            )

            image = None

            if (
                global_index <
                len(self.level_images)
            ):

                image = self.level_images[
                    global_index
                ]

            button = Button(
                level_file
                .replace(
                    ".json",
                    ""
                )
                .upper(),

                position=(x, y),

                size=(160, 80),

                font=self.font,

                callback=lambda path=level_file:
                    self.start_level(path),

                image=image
            )

            self.buttons.append(
                button
            )

    def next_page(self):

        max_page = max(
            0,
            (
                len(self.level_files) - 1
            ) // self.levels_per_page
        )

        if self.current_page < max_page:

            self.current_page += 1
            self.show_page()

    def previous_page(self):

        if self.current_page > 0:

            self.current_page -= 1
            self.show_page()

    def start_level(
        self,
        level_file
    ):

        from .game_scene import GameScene

        level_path = os.path.join(
            "levels",
            level_file
        )

        audio_path = (
            "game/Music/MUSIC.wav"
        )

        p.mixer.music.stop()

        self.scene_manager.change_scene(
            GameScene(
                self.scene_manager,
                level_path
            )
        )

    def handle_events(
        self,
        events
    ):

        for event in events:

            if event.type == p.QUIT:

                p.quit()
                raise SystemExit

            for button in self.buttons:

                button.handle_event(
                    event
                )

            self.next_button.handle_event(
                event
            )

            self.previous_button.handle_event(
                event
            )

    def update(self):
        pass

    def draw(
        self,
        screen
    ):

        screen.fill(
            (0, 0, 0)
        )

        title = self.title_font.render(
            "LEVEL SELECT",
            True,
            (0, 255, 0)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    100
                )
            )
        )

        total_pages = max(
            1,
            (
                len(self.level_files) - 1
            ) //
            self.levels_per_page + 1
        )

        page_text = self.page_font.render(
            (
                f"PAGE "
                f"{self.current_page + 1} / "
                f"{total_pages}"
            ),
            True,
            (255, 255, 255)
        )

        screen.blit(
            page_text,
            page_text.get_rect(
                center=(
                    self.width // 2,
                    self.height - 45
                )
            )
        )

        for button in self.buttons:
            button.draw(screen)

        self.next_button.draw(screen)
        self.previous_button.draw(screen)