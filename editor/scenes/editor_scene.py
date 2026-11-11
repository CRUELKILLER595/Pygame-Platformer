
from pathlib import Path

import pygame as p

from editor.config import (
    EDITOR_VIEW_WIDTH,
    EDITOR_VIEW_HEIGHT,
    SIDEBAR_WIDTH,
)
import tkinter as tk
from tkinter import simpledialog

from pixelbound_core.ui.button import Button
from editor.camera import camera
from editor.palette import Palette
from editor.services.level_service import EditorLevelService
from editor.scenes.base_scene import EditorBaseScene
from pixelbound_core.config.constants import TILE_SIZE
from pixelbound_core.assets.asset_profiles import place_rect_in_cell
from pixelbound_core.graphics.collision import (
    DEBUG_HITBOXES,
    make_collision_rect,
)


from editor.Grid import draw_grid
from editor.mouse import mouse
from editor.undo_redo import Action

class EditorScene(EditorBaseScene):

    def __init__(self, application, level_path):

        self.application = application
        self.scene_manager = application.scene_manager

        self.level_path = Path(level_path)

        # --------------------------------------------------
        # EDITOR SETTINGS
        # --------------------------------------------------

        self.screen_width = EDITOR_VIEW_WIDTH
        self.screen_height = EDITOR_VIEW_HEIGHT

        self.lower_margin = 100
        self.side_margin = SIDEBAR_WIDTH

        self.sidebar_x = self.screen_width
        self.sidebar_width = self.side_margin

        self.camera_speed = 10

        # --------------------------------------------------
        # CAMERA
        # --------------------------------------------------

        self.cam = camera(
            self.screen_width,
            self.screen_height
        )

        # --------------------------------------------------
        # ASSET LIBRARY
        # --------------------------------------------------

        self.asset_library = application.asset_library
        self.ASSETS = application.assets

        self.current_asset = None

        # --------------------------------------------------
        # LEVEL SERVICE
        # --------------------------------------------------

        self.level_service = EditorLevelService(
            self.asset_library
        )

        self.level_data, self.placed_assets = (
            self.level_service.load_level(self.level_path)
        )

        # --------------------------------------------------
        # UNDO / REDO
        # --------------------------------------------------

        self.undo_stack = []
        self.redo_stack = []

        # --------------------------------------------------
        # FONTS
        # --------------------------------------------------

        self.font = p.font.SysFont("Arial", 20)
        self.control_font = p.font.SysFont("Arial", 14)

        # --------------------------------------------------
        # ASSET CATEGORIES
        # --------------------------------------------------

        available_categories = set(
            self.asset_library.get_categories()
        )

        preferred_categories = [
            "CHARACTERS",
            "TRAPS",
            "ENEMIES",
            "TILES",
        ]

        self.option_list = [
            category
            for category in preferred_categories
            if category in available_categories
        ]

        self.option_list.extend(
            sorted(available_categories - set(self.option_list))
        )

        if "CHARACTERS" in self.option_list:
            self.selected_category = "CHARACTERS"
        elif self.option_list:
            self.selected_category = self.option_list[0]
        else:
            self.selected_category = ""

        # --------------------------------------------------
        # CATEGORY DROPDOWN
        # --------------------------------------------------
        # --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------

        self.button_width = 90
        self.button_height = 34

        self.timer_button_rect = p.Rect(
    self.sidebar_x + 8,
    42,
    self.button_width,
    self.button_height
)

        self.timer_button = Button(
    "Set Timer",
    self.timer_button_rect.topleft,
    self.timer_button_rect.size,
    self.control_font,
    self.set_level_timer
)  
        self.dropdown_open = False
        self.dropdown_item_height = 25

        self.dropdown_rect = p.Rect(
            self.sidebar_x + 108,
            21,
            self.sidebar_width - 118,
            34
        )

        # --------------------------------------------------
        # PALETTE
        # --------------------------------------------------

        self.status_y = 80
        self.palette_y = 105

        self.pal = Palette(
            self.ASSETS,
            self.sidebar_x + 10,
            self.palette_y,
            self.sidebar_width - 20,
            self.selected_category
        )

        # --------------------------------------------------
        # PLAYER SPAWN VALIDATION
        # --------------------------------------------------

        self.clean_player_spawns()

        print("STANDALONE EDITOR SCENE CREATED")
        print("Level:", self.level_path.name)
        print("Placed assets:", len(self.placed_assets))
        print("Available assets:", len(self.ASSETS))
        print("Categories:", self.option_list)

    # ======================================================
    # PLAYER HELPERS
    # ======================================================

    def is_player_asset(self, asset):

        return (
            asset is not None
            and asset.role == "player_spawn"
        )

    def get_player_positions(self):

        return [
            position
            for position, asset in self.placed_assets.items()
            if self.is_player_asset(asset)
        ]

    def clean_player_spawns(self):

        player_positions = self.get_player_positions()

        if len(player_positions) <= 1:
            return

        keep_position = player_positions[0]

        print(
            "WARNING: Multiple player spawns found.",
            "Keeping:",
            keep_position
        )

        for position in player_positions[1:]:
            self.placed_assets.pop(position, None)

    # ======================================================
    # GRID HELPERS
    # ======================================================

    def get_tile_from_mouse(self, mouse_x, mouse_y):

        world_x, world_y = self.cam.screen_to_world(
            mouse_x,
            mouse_y
        )

        from pixelbound_core.config.constants import TILE_SIZE

        return (
            int(world_x // TILE_SIZE),
            int(world_y // TILE_SIZE)
        )

    def get_asset_image(self, asset):

        if asset is None or asset.image is None:
            return None

        image = asset.image

        target_size = (
            max(1, int(asset.width)),
            max(1, int(asset.height))
        )

        if image.get_size() != target_size:
            image = p.transform.scale(
                image,
                target_size
            )

        return image
    
    def handle_category_dropdown(self, event):

        if (
            event.type != p.MOUSEBUTTONDOWN
            or event.button != 1
        ):
            return False

        position = event.pos

        if self.dropdown_rect.collidepoint(position):
            self.dropdown_open = not self.dropdown_open
            return True

        if self.dropdown_open:

            for index, category in enumerate(self.option_list):

                option_rect = p.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.bottom
                    + index * self.dropdown_item_height,
                    self.dropdown_rect.width,
                    self.dropdown_item_height
                )

                if option_rect.collidepoint(position):
                    self.selected_category = category
                    self.pal.category = category
                    self.dropdown_open = False
                    return True

            self.dropdown_open = False

        return False

    def draw_category_dropdown(self, screen):

        p.draw.rect(
            screen,
            (242, 242, 242),
            self.dropdown_rect
        )

        p.draw.rect(
            screen,
            (45, 55, 70),
            self.dropdown_rect,
            2
        )

        label = self.selected_category or "No categories"

        if len(label) > 17:
            label = label[:16] + "..."

        header_text = self.control_font.render(
            f"{label}  v",
            True,
            (20, 20, 20)
        )

        screen.blit(
            header_text,
            (
                self.dropdown_rect.x + 6,
                self.dropdown_rect.y + 10
            )
        )

        if not self.dropdown_open:
            return

        for index, category in enumerate(self.option_list):

            option_rect = p.Rect(
                self.dropdown_rect.x,
                self.dropdown_rect.bottom
                + index * self.dropdown_item_height,
                self.dropdown_rect.width,
                self.dropdown_item_height
            )

            option_color = (
                (205, 222, 245)
                if category == self.selected_category
                else (245, 245, 245)
            )

            p.draw.rect(screen, option_color, option_rect)
            p.draw.rect(screen, (75, 75, 75), option_rect, 1)

            display_name = category

            if len(display_name) > 21:
                display_name = display_name[:20] + "..."

            option_text = self.control_font.render(
                display_name,
                True,
                (20, 20, 20)
            )

            screen.blit(
                option_text,
                (
                    option_rect.x + 6,
                    option_rect.y + 5
                )
            )
    
    def set_level_timer(self):

        root = None
        seconds = None

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            current_seconds = int(
                self.level_data.get("timer_seconds", 120)
            )

            seconds = simpledialog.askinteger(
                "Set Level Timer",
                "Enter duration in seconds (1-3600):",
                parent=root,
                initialvalue=current_seconds,
                minvalue=1,
                maxvalue=3600
            )

        except (ValueError, TypeError, tk.TclError) as error:
            print("Could not set timer:", error)
            return

        finally:
            if root is not None:
                try:
                    root.destroy()
                except tk.TclError:
                    pass

        if seconds is None:
            return

        self.level_data["timer_seconds"] = seconds

        print("Timer set to:", seconds, "seconds")

        self.save_level()

    def is_sidebar_control(self, position):

        if self.dropdown_rect.collidepoint(position):
            return True

        if self.dropdown_open:

            menu_rect = p.Rect(
                self.dropdown_rect.x,
                self.dropdown_rect.bottom,
                self.dropdown_rect.width,
                len(self.option_list) * self.dropdown_item_height
            )

            if menu_rect.collidepoint(position):
                return True

        return False
    
    def handle_events(self, events):

        for event in events:

            if event.type == p.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = event.pos

                # Category dropdown gets first priority.
                if event.button == 1:
                    if self.handle_category_dropdown(event):
                        continue

                if self.is_sidebar_control(event.pos):
                    continue

                # LEFT CLICK
                if event.button == 1:

                    # Asset palette selection.
                    if mouse_x >= self.screen_width:

                        clicked_asset = self.pal.get_clicked_asset(
                            event.pos
                        )

                        if clicked_asset is not None:
                            self.current_asset = clicked_asset

                            print(
                                "Selected asset:",
                                self.current_asset.id
                            )

                        continue

                    # Do not place outside the world viewport.
                    if (
                        mouse_y >= self.screen_height
                        or self.current_asset is None
                    ):
                        continue

                    tile_x, tile_y = self.get_tile_from_mouse(
                        mouse_x,
                        mouse_y
                    )

                    position = (tile_x, tile_y)
                    old_asset = self.placed_assets.get(position)

                    # PLAYER SPAWN PLACEMENT
                    if self.is_player_asset(self.current_asset):

                        removed_players = {}

                        for player_position in self.get_player_positions():

                            if player_position == position:
                                continue

                            removed_players[player_position] = (
                                self.placed_assets.pop(player_position)
                            )

                        action = Action(
                            position,
                            old_asset,
                            self.current_asset
                        )

                        action.removed_players = removed_players

                    else:

                        action = Action(
                            position,
                            old_asset,
                            self.current_asset
                        )

                    self.placed_assets[position] = self.current_asset

                    self.undo_stack.append(action)
                    self.redo_stack.clear()

                # RIGHT CLICK: DELETE
                elif event.button == 3:

                    if (
                        mouse_x >= self.screen_width
                        or mouse_y >= self.screen_height
                    ):
                        continue

                    tile_x, tile_y = self.get_tile_from_mouse(
                        mouse_x,
                        mouse_y
                    )

                    position = (tile_x, tile_y)

                    if position not in self.placed_assets:
                        continue

                    old_asset = self.placed_assets[position]

                    action = Action(
                        position,
                        old_asset,
                        None
                    )

                    self.placed_assets.pop(position)

                    self.undo_stack.append(action)
                    self.redo_stack.clear()

            elif event.type == p.KEYDOWN:

                if event.key == p.K_s:
                    self.save_level()

                elif event.key == p.K_ESCAPE:

                    if self.dropdown_open:
                        self.dropdown_open = False
                    else:
                        from editor.scenes.level_select_scene import (
                            EditorLevelSelectScene
                        )

                        self.scene_manager.change_scene(
                            EditorLevelSelectScene(self.application)
                        )

                elif (
                    event.key == p.K_z
                    and p.key.get_mods() & p.KMOD_CTRL
                ):
                    self.undo()

                elif (
                    event.key == p.K_y
                    and p.key.get_mods() & p.KMOD_CTRL
                ):
                    self.redo()

    def update(self):

        keys = p.key.get_pressed()

        if keys[p.K_LEFT]:
            self.cam.x -= self.camera_speed
        elif keys[p.K_RIGHT]:
            self.cam.x += self.camera_speed

        if keys[p.K_UP]:
            self.cam.y -= self.camera_speed
        elif keys[p.K_DOWN]:
            self.cam.y += self.camera_speed

    def undo(self):

        if not self.undo_stack:
            return

        action = self.undo_stack.pop()

        if action.old_asset is None:
            self.placed_assets.pop(action.position, None)
        else:
            self.placed_assets[action.position] = action.old_asset

        removed_players = getattr(
            action,
            "removed_players",
            {}
        )

        for position, asset in removed_players.items():
            self.placed_assets[position] = asset

        self.redo_stack.append(action)

    def redo(self):

        if not self.redo_stack:
            return

        action = self.redo_stack.pop()

        removed_players = getattr(
            action,
            "removed_players",
            {}
        )

        for position in removed_players:
            self.placed_assets.pop(position, None)

        if action.new_asset is None:
            self.placed_assets.pop(action.position, None)
        else:
            self.placed_assets[action.position] = action.new_asset

        self.undo_stack.append(action)

    def save_level(self):

        self.clean_player_spawns()

        try:
            self.level_service.save_level(
                self.level_path,
                self.level_data,
                self.placed_assets
            )

            print("LEVEL SAVED:", self.level_path.name)

        except Exception as error:
            print("Could not save level:", error)

    
    def draw(self, screen):

        screen.fill((25, 25, 30))

        original_clip = screen.get_clip()

        world_rect = p.Rect(
            0,
            0,
            self.screen_width,
            self.screen_height
        )

        # Restrict world rendering to the viewport.
        screen.set_clip(world_rect)

        # --------------------------------------------------
        # GRID
        # --------------------------------------------------

        draw_grid(screen, self.cam)

        # --------------------------------------------------
        # WORLD OBJECTS
        # --------------------------------------------------

        for (grid_x, grid_y), asset in self.placed_assets.items():

            image = self.get_asset_image(asset)

            if image is None:
                continue

            cell_x = round(grid_x * TILE_SIZE)
            cell_y = round(grid_y * TILE_SIZE)

            profile = getattr(asset, "profile", {}) or {}
            anchor = profile.get("anchor", "top_left")

            draw_rect = image.get_rect()

            place_rect_in_cell(
                draw_rect,
                cell_x,
                cell_y,
                TILE_SIZE,
                anchor
            )

            screen_x, screen_y = self.cam.world_to_screen(
                draw_rect.x,
                draw_rect.y
            )

            screen.blit(
                image,
                (int(screen_x), int(screen_y))
            )

            # Collision debug overlay.
            collision_config = profile.get("collision", {})
            collision_box = collision_config.get("box")

            if DEBUG_HITBOXES and collision_box:

                collision_rect = make_collision_rect(
                    draw_rect,
                    collision_box
                )

                hitbox_x, hitbox_y = self.cam.world_to_screen(
                    collision_rect.x,
                    collision_rect.y
                )

                screen_hitbox = p.Rect(
                    int(hitbox_x),
                    int(hitbox_y),
                    collision_rect.width,
                    collision_rect.height
                )

                p.draw.rect(
                    screen,
                    (0, 255, 255),
                    screen_hitbox,
                    2
                )

        # Restore clipping before drawing the UI.
        screen.set_clip(original_clip)

        # --------------------------------------------------
        # SIDEBAR
        # --------------------------------------------------

        sidebar_rect = p.Rect(
            self.sidebar_x,
            0,
            self.sidebar_width,
            screen.get_height()
        )

        p.draw.rect(
            screen,
            (36, 39, 48),
            sidebar_rect
        )

        # --------------------------------------------------
        # PALETTE
        # --------------------------------------------------

        self.pal.draw_palette(screen)

        # --------------------------------------------------
        # SOUNDTRACK STATUS
        # --------------------------------------------------

        soundtrack = self.level_data.get("soundtrack", "")

        track_name = (
            Path(soundtrack).name
            if soundtrack
            else "No track selected"
        )

        track_text = self.control_font.render(
            f"Track: {track_name[:20]}",
            True,
            (240, 240, 240)
        )

        screen.blit(
            track_text,
            (self.sidebar_x + 8, self.status_y)
        )

        # --------------------------------------------------
        # TIMER STATUS
        # --------------------------------------------------

        seconds = int(
            self.level_data.get("timer_seconds", 120)
        )

        minutes, remainder = divmod(seconds, 60)

        timer_text = self.control_font.render(
            f"Timer: {minutes:02d}:{remainder:02d}",
            True,
            (240, 240, 240)
        )

        screen.blit(
            timer_text,
            (self.sidebar_x + 8, self.status_y + 17)
        )

        # --------------------------------------------------
        # CATEGORY DROPDOWN
        # --------------------------------------------------
        self.timer_button.draw(screen)
        self.draw_category_dropdown(screen)

        # --------------------------------------------------
        # MOUSE CURSOR
        # --------------------------------------------------

        mouse(screen)

