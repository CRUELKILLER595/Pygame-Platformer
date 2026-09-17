import pygame as p

from .base_scene import Scene
from .game_scene import GameScene

from ..settings import WIDTH, HEIGHT, FPS, TILE_SIZE

from editor.json_manager import save_level, load_level
from editor.Grid import draw_grid
from editor.mouse import mouse
from editor.camera import camera
from editor.asset_library import load_assets
from editor.palette import Palette
from editor.dropdown import OptionBox
from editor.undo_redo import Action

from ..settings import screen_width


class EditorScene(Scene):

    def __init__(self, scene_manager, level_path):

        self.scene_manager = scene_manager
        self.level_path = level_path

        # --------------------------------------------------
        # EDITOR SETTINGS
        # --------------------------------------------------

        self.screen_width = WIDTH
        self.screen_height = HEIGHT

        self.lower_margin = 100
        self.side_margin = 300

        self.camera_speed = 10

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

        self.ASSETS = load_assets()

        self.current_asset = None

        # --------------------------------------------------
        # LEVEL DATA
        # --------------------------------------------------

        self.level_data = {
            "version": 1,
            "level_name": "Level1",
            "objects": []
        }

        self.placed_assets = {}

        # --------------------------------------------------
        # UNDO / REDO
        # --------------------------------------------------

        self.undo_stack = []
        self.redo_stack = []

        # --------------------------------------------------
        # PALETTE
        # --------------------------------------------------

        self.option_list = [
            "CHARACTERS",
            "TILES"
        ]

        self.font = p.font.SysFont(
            "TimesNewRoman",
            24
        )

        self.Box = OptionBox(
            self.screen_width + 40,
            0,
            200,
            50,
            (255, 255, 255),
            self.font,
            self.option_list
        )

        self.pal = Palette(
            self.ASSETS,
            self.screen_width + 10,
            55,
            300,
            "Characters"
        )

        # --------------------------------------------------
        # LOAD EXISTING LEVEL
        # --------------------------------------------------

        try:

            self.placed_assets = load_level(
                self.ASSETS,
                self.level_path
            )

        except TypeError:

            # Your current load_level() may only accept ASSETS.
            # This keeps compatibility with your old editor.
            self.placed_assets = load_level(
                self.ASSETS
            )

        except Exception as e:

            print("Could not load level:", e)

            self.placed_assets = {}

        print("EDITOR LOADED:", self.level_path)

    # ======================================================
    # EVENTS
    # ======================================================

    def handle_events(self, events):
        selected = self.Box.update(events)

        if selected != -1:
         self.pal.category = selected
        for event in events:

            # ------------------------------------------------
            # QUIT
            # ------------------------------------------------

            if event.type == p.QUIT:

                p.quit()
                raise SystemExit

            # ------------------------------------------------
            # MOUSE
            # ------------------------------------------------

            elif event.type == p.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = p.mouse.get_pos()

                # --------------------------------------------
                # LEFT CLICK
                # --------------------------------------------

                if event.button == 1:

                    # Palette
                    if mouse_x > self.screen_width:

                        clicked_asset = self.pal.get_clicked_asset(
                            (mouse_x, mouse_y)
                        )

                        if clicked_asset is not None:

                            self.current_asset = clicked_asset

                            print(
                                "SELECTED:",
                                self.current_asset.id
                            )

                    # World
                    elif self.current_asset is not None:

                        world_x, world_y = (
                            self.cam.screen_to_world(
                                mouse_x,
                                mouse_y
                            )
                        )

                        tile_x = world_x // TILE_SIZE
                        tile_y = world_y // TILE_SIZE

                        old_asset = self.placed_assets.get(
                            (tile_x, tile_y)
                        )

                        action = Action(
                            (tile_x, tile_y),
                            old_asset,
                            self.current_asset
                        )

                        self.placed_assets[
                            (tile_x, tile_y)
                        ] = self.current_asset

                        self.undo_stack.append(action)

                        self.redo_stack.clear()

                # --------------------------------------------
                # RIGHT CLICK = DELETE
                # --------------------------------------------

                elif event.button == 3:

                    world_x, world_y = (
                        self.cam.screen_to_world(
                            mouse_x,
                            mouse_y
                        )
                    )

                    tile_x = world_x // TILE_SIZE
                    tile_y = world_y // TILE_SIZE

                    if (tile_x, tile_y) in self.placed_assets:

                        old_asset = self.placed_assets[
                            (tile_x, tile_y)
                        ]

                        action = Action(
                            (tile_x, tile_y),
                            old_asset,
                            None
                        )

                        self.placed_assets.pop(
                            (tile_x, tile_y)
                        )

                        self.undo_stack.append(action)

                        self.redo_stack.clear()

            # ------------------------------------------------
            # KEYBOARD
            # ------------------------------------------------

            elif event.type == p.KEYDOWN:

                # ============================================
                # SAVE
                # ============================================

                if event.key == p.K_s:

                    self.save_level()

                # ============================================
                # PLAY MODE
                # ============================================

                elif event.key == p.K_F5:

                    self.play_level()

                # ============================================
                # ESCAPE
                # ============================================

                elif event.key == p.K_ESCAPE:

                    from .menu_scene import MenuScene

                    self.scene_manager.change_scene(
                        MenuScene(
                            self.scene_manager
                        )
                    )

                # ============================================
                # UNDO
                # ============================================

                elif (
                    event.key == p.K_z
                    and p.key.get_mods() & p.KMOD_CTRL
                ):

                    self.undo()

                # ============================================
                # REDO
                # ============================================

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

        # --------------------------------------------------
        # CAMERA
        # --------------------------------------------------

        if keys[p.K_LEFT]:

            self.cam.x -= self.camera_speed

        elif keys[p.K_RIGHT]:

            self.cam.x += self.camera_speed

        if keys[p.K_UP]:

            self.cam.y -= self.camera_speed

        elif keys[p.K_DOWN]:

            self.cam.y += self.camera_speed

        # --------------------------------------------------
        # DROPDOWN
        # --------------------------------------------------

        # Mouse position is needed for palette/dropdown.
        # Events are handled separately.
        pass

    # ======================================================
    # DRAW
    # ======================================================

    def draw(self, screen):

        screen.fill((1, 0, 0))

        # --------------------------------------------------
        # GRID
        # --------------------------------------------------

        draw_grid(
            screen,
            self.cam
        )

        # --------------------------------------------------
        # WORLD OBJECTS
        # --------------------------------------------------

        for (x, y), asset in self.placed_assets.items():

            world_x = x * TILE_SIZE
            world_y = y * TILE_SIZE

            screen_x, screen_y = (
                self.cam.world_to_screen(
                    world_x,
                    world_y
                )
            )

            screen.blit(
                asset.image,
                (screen_x, screen_y)
            )

        # --------------------------------------------------
        # UI
        # --------------------------------------------------

        self.pal.draw_palette(screen)

        mouse(screen)

        self.Box.draw(screen)

    # ======================================================
    # SAVE
    # ======================================================

    def save_level(self):

        print("SAVING:", self.level_path)

        save_level(
            self.level_data,
            self.placed_assets
        )

        print("LEVEL SAVED")

    # ======================================================
    # PLAY MODE
    # ======================================================

    def play_level(self):

        print()
        print("==============================")
        print("ENTERING PLAY MODE")
        print("==============================")
        print()

        # Save before playing
        self.save_level()

        # Switch scene
        self.scene_manager.change_scene(
            GameScene(
                self.scene_manager,
                self.level_path
            )
        )

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

            self.placed_assets.pop(
                position,
                None
            )

        else:

            self.placed_assets[
                position
            ] = old_asset

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

        if new_asset is None:

            self.placed_assets.pop(
                position,
                None
            )

        else:

            self.placed_assets[
                position
            ] = new_asset

        self.undo_stack.append(action)