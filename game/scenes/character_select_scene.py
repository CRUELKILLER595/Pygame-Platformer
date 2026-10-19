
import pygame as p

from .base_scene import Scene
from .level_select_scene import LevelSelectScene

from ..settings import WIDTH, HEIGHT
from ..SpriteLoader import load_sprite_sheets
from..systems.background import TiledBackground
from ..systems.character_registry import (
    CHARACTERS,
    DEFAULT_CHARACTER,
)


class CharacterSelectScene(Scene):

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        self.title_font = p.font.SysFont("Arial", 42)
        self.font = p.font.SysFont("Arial", 24)
        self.small_font = p.font.SysFont("Arial", 17)
        self.background = TiledBackground("Assets/Background/Purple.png")

        self.selected_id = getattr(
            scene_manager,
            "selected_character_id",
            DEFAULT_CHARACTER,
        )

        self.previews = {}
        self.card_rects = {}

        self.load_previews()
        self.create_layout()

    # --------------------------------------------------
    # LOAD CHARACTER PREVIEWS
    # --------------------------------------------------

    def load_previews(self):
        for character_id, config in CHARACTERS.items():

            sprites = load_sprite_sheets(
                "MainCharacters",
                config["sprite_folder"],
                config["frame_width"],
                config["frame_height"],
                True,
            )

            idle_frames = sprites.get("idle_right", [])

            self.previews[character_id] = (
                idle_frames[0] if idle_frames else None
            )

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    def create_layout(self):
        character_ids = list(CHARACTERS.keys())

        gap = 18
        card_width = min(
            230,
            (WIDTH - 80 - gap * (len(character_ids) - 1))
            // len(character_ids),
        )
        card_height = 290

        total_width = (
            len(character_ids) * card_width
            + (len(character_ids) - 1) * gap
        )

        start_x = (WIDTH - total_width) // 2
        card_y = 175

        for index, character_id in enumerate(character_ids):
            x = start_x + index * (card_width + gap)

            self.card_rects[character_id] = p.Rect(
                x,
                card_y,
                card_width,
                card_height,
            )

        self.back_rect = p.Rect(
            40,
            HEIGHT - 80,
            150,
            50,
        )

        self.continue_rect = p.Rect(
            WIDTH // 2 - 110,
            HEIGHT - 80,
            220,
            50,
        )

    # --------------------------------------------------
    # SELECT CHARACTER
    # --------------------------------------------------

    def select_character(self, character_id):
        self.selected_id = character_id

        self.scene_manager.selected_character_id = character_id

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    def handle_events(self, events):
        for event in events:

            if event.type == p.QUIT:
                p.quit()
                raise SystemExit

            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    from .menu_scene import MenuScene

                    self.scene_manager.change_scene(
                        MenuScene(self.scene_manager)
                    )
                    return

            if event.type != p.MOUSEBUTTONDOWN:
                continue

            if event.button != 1:
                continue

            mouse_pos = event.pos

            # Character cards
            for character_id, rect in self.card_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.select_character(character_id)
                    break

            # Back to menu
            if self.back_rect.collidepoint(mouse_pos):
                from .menu_scene import MenuScene

                self.scene_manager.change_scene(
                    MenuScene(self.scene_manager)
                )
                return

            # Continue to level selection
            if self.continue_rect.collidepoint(mouse_pos):
                self.scene_manager.selected_character_id = (
                    self.selected_id
                )

                self.scene_manager.change_scene(
                    LevelSelectScene(self.scene_manager)
                )
                return

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update(self):
        pass

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------

    def draw(self, screen):
        self.background.draw(screen)

        title = self.title_font.render(
            "CHOOSE YOUR CHARACTER",
            True,
            (0, 0, 0),
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 65)
            ),
        )

        subtitle = self.small_font.render(
            "Select your hero before starting a level",
            True,
            (190, 200, 220),
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, 120)
            ),
        )

        # Draw character cards
        for character_id, config in CHARACTERS.items():

            rect = self.card_rects[character_id]
            selected = character_id == self.selected_id

            card_color = (
                (48, 75, 90)
                if selected
                else (39, 46, 63)
            )

            border_color = (
                (100, 230, 165)
                if selected
                else (95, 110, 135)
            )

            p.draw.rect(
                screen,
                card_color,
                rect,
                border_radius=12,
            )

            p.draw.rect(
                screen,
                border_color,
                rect,
                width=4 if selected else 1,
                border_radius=12,
            )

            # Character sprite
            preview = self.previews.get(character_id)

            if preview is not None:
                # Enlarge the sprite for the card preview.
                preview_image = p.transform.scale(
                    preview,
                    (
                        preview.get_width() * 3,
                        preview.get_height() * 3,
                    ),
                )

                preview_rect = preview_image.get_rect(
                    center=(rect.centerx, rect.y + 115)
                )

                screen.blit(preview_image, preview_rect)

            # Character name
            name = config.get(
                "display_name",
                character_id.replace("_", " ").title(),
            )

            name_text = self.font.render(
                name,
                True,
                (255, 255, 255),
            )

            screen.blit(
                name_text,
                name_text.get_rect(
                    center=(rect.centerx, rect.y + 210)
                ),
            )

            status = (
                "SELECTED"
                if selected
                else "CLICK TO SELECT"
            )

            status_text = self.small_font.render(
                status,
                True,
                (130, 240, 180) if selected
                else (185, 195, 215),
            )

            screen.blit(
                status_text,
                status_text.get_rect(
                    center=(rect.centerx, rect.y + 255)
                ),
            )

        # Back button
        p.draw.rect(
            screen,
            (65, 75, 95),
            self.back_rect,
            border_radius=8,
        )

        back_text = self.font.render(
            "Back",
            True,
            (255, 255, 255),
        )

        screen.blit(
            back_text,
            back_text.get_rect(
                center=self.back_rect.center
            ),
        )

        # Continue button
        p.draw.rect(
            screen,
            (45, 145, 95),
            self.continue_rect,
            border_radius=8,
        )

        continue_text = self.font.render(
            "Continue",
            True,
            (255, 255, 255),
        )

        screen.blit(
            continue_text,
            continue_text.get_rect(
                center=self.continue_rect.center
            ),
        )
