import pygame as p

from .base_scene import Scene
from ui.button import Button
from ui.Slider import Slider

from ..settings import WIDTH, HEIGHT

from ..systems.settings_manager import (
    SettingsManager
)

from ..systems.audio_manager import (
    audio_manager
)


settings_manager = SettingsManager()


class SettingsScene(Scene):

    def __init__(
        self,
        scene_manager,
        return_scene
    ):

        self.scene_manager = scene_manager
        self.return_scene = return_scene

        self.title_font = p.font.SysFont(
            "Arial",
            50
        )

        self.font = p.font.SysFont(
            "Arial",
            26
        )

        self.music_slider = Slider(
            350,
            250,
            400,
            settings_manager.music_volume
        )

        self.sfx_slider = Slider(
            350,
            350,
            400,
            settings_manager.sfx_volume
        )

        self.brightness_slider = Slider(
            350,
            450,
            400,
            settings_manager.brightness
        )

        self.back_button = Button(
            "Back",
            (
                WIDTH // 2 - 100,
                540
            ),
            (200, 50),
            self.font,
            self.go_back
        )

    def handle_events(
        self,
        events
    ):

        for event in events:

            if event.type == p.QUIT:

                p.quit()
                raise SystemExit

            self.music_slider.handle_event(
                event
            )

            self.sfx_slider.handle_event(
                event
            )

            self.brightness_slider.handle_event(
                event
            )

            self.back_button.handle_event(
                event
            )

    def update(self):

        settings_manager.set_music_volume(
            self.music_slider.value
        )

        settings_manager.set_sfx_volume(
            self.sfx_slider.value
        )

        settings_manager.set_brightness(
            self.brightness_slider.value
        )

        audio_manager.set_music_volume(
            self.music_slider.value
        )

        audio_manager.set_sfx_volume(
            self.sfx_slider.value
        )

    def go_back(self):

        self.scene_manager.change_scene(
            self.return_scene
        )

    def draw(
        self,
        screen
    ):

        screen.fill(
            (30, 30, 30)
        )

        title = self.title_font.render(
            "SETTINGS",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    WIDTH // 2,
                    100
                )
            )
        )

        labels = [
            ("Music Volume", 210),
            ("SFX Volume", 310),
            ("Brightness", 410)
        ]

        for text, y in labels:

            label = self.font.render(
                text,
                True,
                (255, 255, 255)
            )

            screen.blit(
                label,
                (350, y)
            )

        self.music_slider.draw(
            screen
        )

        self.sfx_slider.draw(
            screen
        )

        self.brightness_slider.draw(
            screen
        )

        self.back_button.draw(
            screen
        )