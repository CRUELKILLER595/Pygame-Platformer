import pygame as p

from .base_scene import Scene

from ..settings import WIDTH, HEIGHT


class EndScene(Scene):

    def __init__(
        self,
        scene_manager,
        score_manager
    ):

        self.scene_manager = scene_manager
        self.score_manager = score_manager

        self.title_font = p.font.SysFont(
            "Arial",
            64
        )

        self.score_font = p.font.SysFont(
            "Arial",
            40
        )

    def handle_events(
        self,
        events
    ):

        for event in events:

            if event.type == p.QUIT:

                p.quit()
                raise SystemExit

    def update(self):

        pass

    def draw(
        self,
        screen
    ):

        screen.fill(
            (20, 20, 20)
        )

        title = self.title_font.render(
            "LEVEL COMPLETE!",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 80
            )
        )

        screen.blit(
            title,
            title_rect
        )

        score = self.score_font.render(
            f"SCORE: {self.score_manager.score}",
            True,
            (255, 255, 255)
        )

        score_rect = score.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2
            )
        )

        screen.blit(
            score,
            score_rect
        )