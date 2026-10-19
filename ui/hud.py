import pygame as p


class HUD:

    def __init__(
        self,
        score_manager,
        game_timer
    ):

        self.score_manager = score_manager
        self.game_timer = game_timer

        self.font = p.font.SysFont(
            "Arial",
            24
        )

    def draw(self, screen):

        score_text = self.font.render(
            f"SCORE: {self.score_manager.score}",
            True,
            (255, 255, 255)
        )

        time_text = self.font.render(
            f"TIME: {self.game_timer.get_time()}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            score_text,
            (20, 80)
        )

        screen.blit(
            time_text,
            (20, 110)
        )