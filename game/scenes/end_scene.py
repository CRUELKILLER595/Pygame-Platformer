import pygame as p
from pathlib import Path

from .base_scene import Scene
from ..settings import WIDTH, HEIGHT
from ui.button import Button
from ..systems.online_client import download_level_to_cache
from ..systems.audio_manager import audio_manager

class EndScene(Scene):
    def __init__(
        self,
        scene_manager,
        score_manager,
        current_level_metadata=None,
        next_level_metadata=None,
        level_catalog=None,
    ):
        self.scene_manager = scene_manager
        self.score_manager = score_manager
        self.current_level_metadata = dict(current_level_metadata or {})
        self.next_level_metadata = (
            dict(next_level_metadata)
            if next_level_metadata is not None
            else None
        )
        self.level_catalog = [
            dict(level) for level in (level_catalog or [])
        ]

        self.title_font = p.font.SysFont("Arial", 64)
        self.score_font = p.font.SysFont("Arial", 40)
        self.message_font = p.font.SysFont("Arial", 24)
        self.button_font = p.font.SysFont("Arial", 28)
        self.message = ""

        self.next_button = None
        if self.next_level_metadata is not None:
            self.next_button = Button(
                text="Next Level",
                position=(WIDTH // 2 - 110, HEIGHT // 2 + 80),
                size=(220, 58),
                font=self.button_font,
                callback=self.next_level,
            )

        self.menu_button = Button(
            text="Level Select",
            position=(WIDTH // 2 - 110, HEIGHT // 2 + 155),
            size=(220, 58),
            font=self.button_font,
            callback=self.go_to_level_select,
        )

    def handle_events(self, events):
        for event in events:
            if event.type == p.QUIT:
                p.quit()
                raise SystemExit

            if self.next_button is not None:
                self.next_button.handle_event(event)
            self.menu_button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 20))

        title = self.title_font.render(
            "LEVEL COMPLETE!", True, (255, 255, 255)
        )
        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 125)),
        )

        score = self.score_font.render(
            f"SCORE: {self.score_manager.score}",
            True,
            (255, 255, 255),
        )
        screen.blit(
            score,
            score.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 55)),
        )

        if self.next_button is not None:
            self.next_button.draw(screen)
        else:
            message = self.message_font.render(
                "No further playable levels are available yet.",
                True,
                (220, 220, 220),
            )
            screen.blit(
                message,
                message.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)),
            )

        self.menu_button.draw(screen)

        if self.message:
            error_text = self.message_font.render(
                self.message, True, (255, 120, 120)
            )
            screen.blit(
                error_text,
                error_text.get_rect(center=(WIDTH // 2, HEIGHT - 30)),
            )

    def next_level(self):
        level = self.next_level_metadata
        if level is None:
            self.go_to_level_select()
            return

        if not level.get("playable", False):
            self.message = "This level is not playable yet."
            return

        try:
            if level.get("source") == "online":
                level_path = download_level_to_cache(level["id"])
            else:
                filename = level.get("filename") or f"{level['id']}.json"
                level_path = str(Path("levels") / filename)
        except Exception as exc:
            print("Could not load next level:", exc)
            self.message = "Could not download the next level. Try again."
            return

        # Import here to avoid a module-level scene import cycle.
        from .game_scene import GameScene

        self.scene_manager.change_scene(
            GameScene(
                self.scene_manager,
                level_path,
                level_metadata=level,
                level_catalog=self.level_catalog,
            )
        )

    def go_to_level_select(self):
        from .level_select_scene import LevelSelectScene
        audio_manager.stop_music()
        audio_manager.play_music("menu")
        self.scene_manager.change_scene(LevelSelectScene(self.scene_manager))
