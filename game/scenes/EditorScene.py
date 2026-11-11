
import inspect
import json
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, simpledialog

import pygame as p

from ui.button import Button

from .base_scene import Scene
from .game_scene import GameScene
from pixelbound_core.assets.asset_profiles import place_rect_in_cell
from ..systems.collision_profiles import DEBUG_HITBOXES, make_collision_rect
from ..settings import WIDTH, HEIGHT, TILE_SIZE
from ..systems.asset_manager import AssetManager
from ..objects.player import Player

from editor.json_manager import (
    save_level as write_level_file,
    load_level,
)
from editor.Grid import draw_grid
from editor.mouse import mouse
from editor.camera import camera
from editor.palette import Palette
from editor.undo_redo import Action


class EditorScene(Scene):

    def __init__(self, scene_manager, level_path):

        self.scene_manager = scene_manager
        self.level_path = Path(level_path)

        # --------------------------------------------------
        # EDITOR SETTINGS
        # --------------------------------------------------

        self.screen_width = WIDTH
        self.screen_height = HEIGHT

        self.lower_margin = 100
        self.side_margin = 300
        self.camera_speed = 10

        self.sidebar_x = self.screen_width
        self.sidebar_width = self.side_margin
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

        # --------------------------------------------------
        # CAMERA
        # --------------------------------------------------

        self.cam = camera(
            self.screen_width,
            self.screen_height
        )

        # --------------------------------------------------
        # ASSETS
        # --------------------------------------------------

        self.asset_manager = AssetManager()
        self.ASSETS = self.asset_manager.load_all()

        self.current_asset = None

        # --------------------------------------------------
        # LEVEL METADATA
        # --------------------------------------------------

        self.level_data = {
            "version": 1,
            "level_name": self.level_path.stem,
            "soundtrack": "",
            "timer_seconds": 120,
            "objects": [],
        }

        # Restore saved settings if this level already exists.
        if self.level_path.is_file():
            try:
                with self.level_path.open(
                    "r",
                    encoding="utf-8"
                ) as file:
                    existing_data = json.load(file)

                if isinstance(existing_data, dict):
                    self.level_data.update({
                        key: value
                        for key, value in existing_data.items()
                        if key != "objects"
                    })

            except (OSError, json.JSONDecodeError) as error:
                print("Could not load level settings:", error)

        # Migrate the older field name.
        if not self.level_data.get("soundtrack"):
            self.level_data["soundtrack"] = (
                self.level_data.get("soundtracks", "")
            )

        self.level_data.pop("soundtracks", None)
        self.level_data.setdefault("timer_seconds", 120)

        # --------------------------------------------------
        # PLACED OBJECTS AND UNDO/REDO
        # --------------------------------------------------

        self.placed_assets = {}

        self.undo_stack = []
        self.redo_stack = []

        # --------------------------------------------------
        # FONTS AND SIDEBAR CONTROLS
        # --------------------------------------------------

        self.font = p.font.SysFont("Arial", 20)
        self.control_font = p.font.SysFont("Arial", 14)

        self.button_width = 90
        self.button_height = 34

        self.soundtrack_button_rect = p.Rect(
            self.sidebar_x + 8,
            4,
            self.button_width,
            self.button_height
        )

        self.timer_button_rect = p.Rect(
            self.sidebar_x + 8,
            42,
            self.button_width,
            self.button_height
        )

        self.add_soundtrack_button = Button(
            "Soundtrack",
            self.soundtrack_button_rect.topleft,
            self.soundtrack_button_rect.size,
            self.control_font,
            self.add_soundtrack
        )

        self.add_timer_button = Button(
            "Set Timer",
            self.timer_button_rect.topleft,
            self.timer_button_rect.size,
            self.control_font,
            self.set_level_timer
        )

        # --------------------------------------------------
        # CATEGORY DROPDOWN
        # --------------------------------------------------

        # --------------------------------------------------
# CATEGORY DROPDOWN
# --------------------------------------------------

        available_categories = set(
    self.asset_manager.get_categories()
)

# Show these categories first, in this order.
        preferred_categories = [
    "CHARACTERS",
    "TRAPS",
    "ENEMIES",
    "TILES"
]

        self.option_list = [
    category
    for category in preferred_categories
    if category in available_categories
]

# Preserve all other existing asset categories.
        self.option_list.extend(
    sorted(
        available_categories - set(self.option_list)
    )
)

        print("EDITOR CATEGORIES:", self.option_list)

        print(
    "ENEMY ASSETS:",
    len(
        self.asset_manager.get_by_category("ENEMIES")
    )
)

        if "CHARACTERS" in self.option_list:
            self.selected_category = "CHARACTERS"
        elif self.option_list:
            self.selected_category = self.option_list[0]
        else:
            self.selected_category = ""

        self.dropdown_open = False
        self.dropdown_item_height = 25

        self.dropdown_rect = p.Rect(
            self.sidebar_x + 108,
            21,
            self.sidebar_width - 118,
            34
        )

        self.status_y = 80
        self.palette_y = 105

        self.pal = Palette(
            self.ASSETS,
            self.sidebar_x + 10,
            self.palette_y,
            self.sidebar_width - 20,
            self.selected_category
        )

        print("ASSET CATEGORIES:", self.option_list)
        print("TOTAL ASSETS:", len(self.ASSETS))

        # --------------------------------------------------
        # LOAD SAVED LEVEL OBJECTS
        # --------------------------------------------------

        try:
            self.placed_assets = load_level(
                self.ASSETS,
                self.level_path
            )

        except TypeError:
            # Compatibility with an older json_manager.py.
            try:
                self.placed_assets = load_level(self.ASSETS)
            except Exception as error:
                print("Could not load level objects:", error)
                self.placed_assets = {}

        except Exception as error:
            print("Could not load level objects:", error)
            self.placed_assets = {}

        self.clean_player_spawns()

        print("EDITOR LOADED:", self.level_path)

    # ======================================================
    # PLAYER HELPERS
    # ======================================================

    def is_player_asset(self, asset):

        return (
            asset is not None
            and asset.object_class == Player
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

        return (
            int(world_x // TILE_SIZE),
            int(world_y // TILE_SIZE)
        )

    def get_asset_image(self, asset):

        if asset is None or asset.image is None:
            return None

        image = asset.image

        target_width = max(1, int(asset.width))
        target_height = max(1, int(asset.height))

        if image.get_size() != (
            target_width,
            target_height
        ):
            image = p.transform.scale(
                image,
                (target_width, target_height)
            )

        return image

    # ======================================================
    # CATEGORY DROPDOWN
    # ======================================================

    def handle_category_dropdown(self, event):

        if (
            event.type != p.MOUSEBUTTONDOWN
            or event.button != 1
        ):
            return False

        position = event.pos

        # Open or close the dropdown header.
        if self.dropdown_rect.collidepoint(position):
            self.dropdown_open = not self.dropdown_open
            return True

        # Handle a category selection.
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

                    print("Selected category:", category)
                    return True

            # A click outside the menu closes it.
            self.dropdown_open = False

        return False

    def draw_category_dropdown(self, screen):

        # Header.
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

        # Draw options over the palette.
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

    def is_sidebar_control(self, position):

        if (
            self.soundtrack_button_rect.collidepoint(position)
            or self.timer_button_rect.collidepoint(position)
            or self.dropdown_rect.collidepoint(position)
        ):
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

    # ======================================================
    # EVENTS
    # ======================================================

    def handle_events(self, events):

        for event in events:

            # QUIT
            if event.type == p.QUIT:
                p.quit()
                raise SystemExit

            # BUTTONS
            self.add_soundtrack_button.handle_event(event)
            self.add_timer_button.handle_event(event)

            # CATEGORY DROPDOWN
            if self.handle_category_dropdown(event):
                continue

            # MOUSE
            if event.type == p.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = event.pos

                # Ignore clicks on sidebar controls.
                if self.is_sidebar_control(event.pos):
                    continue

                # LEFT CLICK
                if event.button == 1:

                    # Sidebar palette.
                    if mouse_x >= self.screen_width:

                        clicked_asset = self.pal.get_clicked_asset(
                            (mouse_x, mouse_y)
                        )

                        if clicked_asset is not None:
                            self.current_asset = clicked_asset

                            print(
                                "SELECTED ASSET:",
                                self.current_asset.id
                            )

                        continue

                    # Only place assets inside the world viewport.
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

                    # PLAYER PLACEMENT
                    if self.is_player_asset(self.current_asset):

                        removed_players = {}

                        for player_position in self.get_player_positions():

                            if player_position == position:
                                continue

                            removed_players[player_position] = (
                                self.placed_assets[player_position]
                            )

                            self.placed_assets.pop(
                                player_position,
                                None
                            )

                        action = Action(
                            position,
                            old_asset,
                            self.current_asset
                        )

                        action.removed_players = removed_players

                        self.placed_assets[position] = self.current_asset

                        self.undo_stack.append(action)
                        self.redo_stack.clear()

                        print("PLAYER SPAWN SET TO:", position)

                    # NORMAL ASSET PLACEMENT
                    else:

                        action = Action(
                            position,
                            old_asset,
                            self.current_asset
                        )

                        self.placed_assets[position] = self.current_asset

                        self.undo_stack.append(action)
                        self.redo_stack.clear()

                # RIGHT CLICK = DELETE WORLD OBJECT
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

                    self.placed_assets.pop(position, None)

                    self.undo_stack.append(action)
                    self.redo_stack.clear()

                continue

            # KEYBOARD
            if event.type == p.KEYDOWN:

                if event.key == p.K_s:
                    self.save_level()

                elif event.key == p.K_F5:
                    self.play_level()

                elif event.key == p.K_ESCAPE:

                    if self.dropdown_open:
                        self.dropdown_open = False
                    else:
                        from .menu_scene import MenuScene

                        self.scene_manager.change_scene(
                            MenuScene(self.scene_manager)
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

    # ======================================================
    # UPDATE
    # ======================================================

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

    # ======================================================
    # DRAW
    # ======================================================

    
    def draw(self, screen):

     screen.fill((25, 25, 30))

    # Save the original clipping region.
     original_clip = screen.get_clip()

     world_rect = p.Rect(
        0,
        0,
        self.screen_width,
        self.screen_height
    )

    # Restrict grid and world objects to the game viewport.
     screen.set_clip(world_rect)

    # --------------------------------------------------
    # GRID
    # --------------------------------------------------

     draw_grid(screen, self.cam)

    # --------------------------------------------------
    # WORLD OBJECTS
    # --------------------------------------------------

     for (grid_x, grid_y), asset in self.placed_assets.items():

        image = getattr(asset, "image", None)

        if image is None:
            continue

        cell_x = round(grid_x * TILE_SIZE)
        cell_y = round(grid_y * TILE_SIZE)

        # Read this asset's placement configuration.
        profile = getattr(asset, "profile", {}) or {}
        anchor = profile.get("anchor", "top_left")

        # Position the existing rendered image inside its cell.
        draw_rect = image.get_rect()

        place_rect_in_cell(
            draw_rect,
            cell_x,
            cell_y,
            TILE_SIZE,
            anchor,
        )

        # Convert world coordinates to screen coordinates.
        screen_x, screen_y = self.cam.world_to_screen(
            draw_rect.x,
            draw_rect.y,
        )

        screen.blit(
            image,
            (int(screen_x), int(screen_y))
        )

        # --------------------------------------------------
        # COLLISION DEBUG OVERLAY
        # --------------------------------------------------

        collision_config = profile.get("collision", {})
        collision_box = collision_config.get("box")

        if DEBUG_HITBOXES and collision_box:

            collision_rect = make_collision_rect(
                draw_rect,
                collision_box,
            )

            hitbox_x, hitbox_y = self.cam.world_to_screen(
                collision_rect.x,
                collision_rect.y,
            )

            screen_hitbox = p.Rect(
                int(hitbox_x),
                int(hitbox_y),
                collision_rect.width,
                collision_rect.height,
            )

            p.draw.rect(
                screen,
                (0, 255, 255),
                screen_hitbox,
                2,
            )

    # Restore clipping before rendering editor UI.
     screen.set_clip(original_clip)

    # --------------------------------------------------
    # SIDEBAR BACKGROUND
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
    # ASSET PALETTE
    # --------------------------------------------------

     self.pal.draw_palette(screen)

    # --------------------------------------------------
    # HEADER CONTROLS
    # --------------------------------------------------

     self.add_soundtrack_button.draw(screen)
     self.add_timer_button.draw(screen)

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

     self.draw_category_dropdown(screen)
 
    # --------------------------------------------------
    # MOUSE
    # --------------------------------------------------

     mouse(screen)


    def add_soundtrack(self):

        root = None
        selected_file = ""

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            selected_file = filedialog.askopenfilename(
                parent=root,
                title="Select Level Soundtrack",
                filetypes=[
                    ("WAV Audio Files", "*.wav")
                ]
            )

        except Exception as error:
            print("Could not open file picker:", error)
            return

        finally:
            if root is not None:
                try:
                    root.destroy()
                except tk.TclError:
                    pass

        if not selected_file:
            return

        try:
            project_root = Path(__file__).resolve().parents[2]
            music_dir = project_root / "game" / "Music"
            music_dir.mkdir(parents=True, exist_ok=True)

            source = Path(selected_file).resolve()

            if source.suffix.lower() != ".wav":
                print("Please select a WAV file.")
                return

            target = music_dir / source.name
            counter = 1

            # Avoid overwriting a different existing file.
            while target.exists() and target.resolve() != source:
                target = music_dir / (
                    f"{source.stem}_{counter}{source.suffix}"
                )
                counter += 1

            if source != target.resolve():
                shutil.copy2(source, target)

            self.level_data["soundtrack"] = (
                target.relative_to(project_root).as_posix()
            )

            print(
                "Selected soundtrack:",
                self.level_data["soundtrack"]
            )

            self.save_level()

        except (OSError, ValueError) as error:
            print("Could not set soundtrack:", error)

    # ======================================================
    # LEVEL TIMER
    # ======================================================

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

    # ======================================================
    # SAVE LEVEL
    # ======================================================

    def save_level(self):

        print("SAVING:", self.level_path)

        try:
            write_level_file(
                self.level_data,
                self.placed_assets,
                self.level_path
            )

            print("LEVEL SAVED")

        except TypeError:
            print(
                "Your editor/json_manager.py save_level() "
                "must accept level_data, placed_assets, and "
                "level_path."
            )

        except Exception as error:
            print("Could not save level:", error)

    # ======================================================
    # PLAY MODE
    # ======================================================

    def play_level(self):

        print()
        print("==============================")
        print("ENTERING PLAY MODE")
        print("==============================")
        print()

        self.clean_player_spawns()
        self.save_level()

        # Support GameScene variants with or without next_level_path.
        try:
            parameters = inspect.signature(GameScene).parameters
        except (TypeError, ValueError):
            parameters = {}

        if "next_level_path" in parameters:
            game_scene = GameScene(
                self.scene_manager,
                str(self.level_path),
                getattr(self, "next_level_path", None)
            )
        else:
            game_scene = GameScene(
                self.scene_manager,
                str(self.level_path)
            )

        self.scene_manager.change_scene(game_scene)

    # ======================================================
    # UNDO
    # ======================================================

    def undo(self):

        if not self.undo_stack:
            return

        action = self.undo_stack.pop()

        position = action.position
        old_asset = action.old_asset

        if old_asset is None:
            self.placed_assets.pop(position, None)
        else:
            self.placed_assets[position] = old_asset

        removed_players = getattr(
            action,
            "removed_players",
            {}
        )

        for player_position, player_asset in removed_players.items():
            self.placed_assets[player_position] = player_asset

        self.redo_stack.append(action)

    # ======================================================
    # REDO
    # ======================================================

    def redo(self):

        if not self.redo_stack:
            return

        action = self.redo_stack.pop()

        position = action.position
        new_asset = action.new_asset

        removed_players = getattr(
            action,
            "removed_players",
            {}
        )

        for player_position in removed_players:
            self.placed_assets.pop(player_position, None)

        if new_asset is None:
            self.placed_assets.pop(position, None)
        else:
            self.placed_assets[position] = new_asset

        self.undo_stack.append(action)
