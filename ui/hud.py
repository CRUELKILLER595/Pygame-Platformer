import pygame as p


class HUD:

    FRUIT_ORDER = (
        "Apple",
        "Bananas",
        "Cherries",
        "Kiwi",
        "Melon",
        "Orange",
        "Pineapple",
        "Strawberry",
    )

    def __init__(self, score_manager, game_timer):
        self.score_manager = score_manager
        self.game_timer = game_timer

        self.font = p.font.SysFont("Arial", 24)
        self.title_font = p.font.SysFont("Arial", 16, bold=True)
        self.fruit_font = p.font.SysFont("Arial", 12)
        self.counter_font = p.font.SysFont("Arial", 17, bold=True)

        # Maps each fruit name to its HUD icon.
        self.fruit_icons = {}

        self.panel_color = (27, 38, 50)
        self.panel_border = (75, 91, 106)
        self.text_color = (255, 255, 255)

    def set_fruit_assets(self, fruit_assets):
        """Load the preview image for each fruit into the HUD."""

        self.fruit_icons.clear()

        for asset in fruit_assets:
            if asset.image is None:
                continue

            fruit_name = asset.name.strip().casefold()

            icon = p.transform.smoothscale(
                asset.image,
                (24, 24)
            )

            self.fruit_icons[fruit_name] = icon

    def get_fruit_count(self, fruit_name):
        """Get the collected count, ignoring name capitalization."""

        for name, count in self.score_manager.fruit_counts.items():
            if name.casefold() == fruit_name.casefold():
                return count

        return 0

    def draw(self, screen):

        # -------------------------------
        # SCORE
        # -------------------------------
        score_text = self.font.render(
            f"SCORE: {self.score_manager.score}",
            True,
            self.text_color
        )

        screen.blit(score_text, (20, 80))

        # -------------------------------
        # TIMER
        # -------------------------------
        time_text = self.font.render(
            f"TIME: {self.game_timer.get_time()}",
            True,
            self.text_color
        )

        screen.blit(time_text, (20, 110))

        # -------------------------------
        # FRUIT COLLECTION PANEL
        # -------------------------------
        panel_width = min(360, screen.get_width() - 20)
        panel_height = 106

        panel_x = max(
            10,
            screen.get_width() - panel_width - 20
        )
        panel_y = 15

        panel_rect = p.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        p.draw.rect(
            screen,
            self.panel_color,
            panel_rect,
            border_radius=8
        )

        p.draw.rect(
            screen,
            self.panel_border,
            panel_rect,
            width=1,
            border_radius=8
        )

        title = self.title_font.render(
            "FRUIT COLLECTION",
            True,
            self.text_color
        )

        screen.blit(
            title,
            (panel_x + 10, panel_y + 5)
        )

        # Display eight fruit types in two rows.
        inner_width = panel_width - 16
        cell_width = inner_width / 4

        for index, fruit_name in enumerate(self.FRUIT_ORDER):

            column = index % 4
            row = index // 4

            item_x = int(panel_x + 8 + column * cell_width)
            item_y = panel_y + 25 + row * 37

            # Draw the fruit image.
            icon = self.fruit_icons.get(fruit_name.casefold())

            if icon is not None:
                screen.blit(icon, (item_x, item_y))

            # Draw its individual collection count.
            count = self.get_fruit_count(fruit_name)

            count_text = self.counter_font.render(
                f"x{count}",
                True,
                self.text_color
            )

            screen.blit(
                count_text,
                (item_x + 26, item_y + 2)
            )

            # Draw the fruit name under its image.
            name_text = self.fruit_font.render(
                fruit_name,
                True,
                (200, 212, 222)
            )

            screen.blit(
                name_text,
                (item_x, item_y + 23)
            )