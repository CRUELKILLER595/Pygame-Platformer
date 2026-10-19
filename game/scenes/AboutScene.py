from.base_scene import Scene
from ..settings import WIDTH, HEIGHT
from ui.button import Button
from..systems.background import TiledBackground
import pygame as p


class AboutScene(Scene):
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.width = WIDTH
        self.height = HEIGHT

        self.font = p.font.SysFont("Times New Roman", 42)
        self.title_font = p.font.SysFont("Arial", 64)
        self.button_font = p.font.SysFont("Arial", 28)
        self.background = TiledBackground("assets/Background/Gray.png")

        self.about_text = (
            "PixelBound is a 2D platformer where players explore levels, "
            "overcome obstacles, collect fruits, and avoid dangerous traps. "
            "With checkpoints, animated objects, and progressively "
            "challenging gameplay, PixelBound aims to deliver a fun "
            "and engaging platforming experience."
        )

        self.back_button = Button(
            text="Back",
            position=(WIDTH // 2 - 110, HEIGHT - 100),
            size=(220, 58),
            font=self.button_font,
            callback=self.go_to_menu,
        )
    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines
    def go_to_menu(self):
        from.menu_scene import MenuScene
        self.scene_manager.change_scene(MenuScene)
    def handle_events(self, events):
        for event in events:
            if event.type == p.QUIT:
                p.quit()
                raise SystemExit
            self.back_button.handle_event(event)

    def draw(self, screen):
        self.background.draw(screen)

        title = self.title_font.render(
            "ABOUT PIXELBOUND", True, (0, 255, 0)
        )
        screen.blit(
            title,
            title.get_rect(center=(self.width // 2, 100)),
        )

        # Render the about text
        lines = self.wrap_text(self.about_text, self.font, self.width - 40)
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (0, 0, 0))
            screen.blit(
                text_surface,
                (20, 200 + i * (self.font.get_height() + 5)),
            )

        self.back_button.draw(screen)

    def update(self):
        pass