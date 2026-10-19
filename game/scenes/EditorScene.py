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
from ..systems.asset_manager import AssetManager,Asset
from ..objects.player import Player

from ..settings import screen_width


class EditorScene(Scene):

    def __init__(self, scene_manager, level_path):

        self.scene_manager = scene_manager
        self.level_path = level_path
        self.asset_manager=AssetManager()

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

        self.ASSETS = self.asset_manager.load_all()

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

        self.option_list =self.asset_manager.get_categories()
        print("ASSETS TYPE:", type(self.ASSETS))
        print("CATEGORIES:", self.option_list)

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
            "CHARACTERS"
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

            self.placed_assets = load_level(
                self.ASSETS
            )

        except Exception as e:

            print("Could not load level:", e)

            self.placed_assets = {}

        # --------------------------------------------------
        # CLEAN EXISTING PLAYER DUPLICATES
        # --------------------------------------------------

        self.clean_player_spawns()

        print("EDITOR LOADED:", self.level_path)

    # ======================================================
    # PLAYER HELPERS
    # ======================================================

    def is_player_asset(self, asset):

        if asset is None:
            return False

        return asset.object_class == Player

    def get_player_positions(self):

        positions = []

        for position, asset in self.placed_assets.items():

            if self.is_player_asset(asset):
                positions.append(position)

        return positions

    def clean_player_spawns(self):

        player_positions = self.get_player_positions()

        if len(player_positions) <= 1:
            return

        # Keep the first player.
        keep_position = player_positions[0]

        print(
            "WARNING: Multiple player spawns found.",
            "Keeping:",
            keep_position
        )

        for position in player_positions[1:]:

            self.placed_assets.pop(
                position,
                None
            )

    # ======================================================
    # GRID HELPERS
    # ======================================================

    def get_tile_from_mouse(self, mouse_x, mouse_y):

        world_x, world_y = (
            self.cam.screen_to_world(
                mouse_x,
                mouse_y
            )
        )

        # Force integer grid coordinates.
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        return tile_x, tile_y

    def get_asset_image(self, asset):

        if asset is None:
            return None

        image = asset.image

        target_width = int(asset.width)
        target_height = int(asset.height)

        if (
            image.get_width() != target_width
            or
            image.get_height() != target_height
        ):

            image = p.transform.scale(
                image,
                (
                    target_width,
                    target_height
                )
            )

        return image

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

                    # ----------------------------------------
                    # PALETTE
                    # ----------------------------------------

                    if mouse_x > self.screen_width:

                        clicked_asset = (
                            self.pal.get_clicked_asset(
                                (mouse_x, mouse_y)
                            )
                        )

                        if clicked_asset is not None:

                            self.current_asset = clicked_asset

                            print(
                                "SELECTED:",
                                self.current_asset.id
                            )

                    # ----------------------------------------
                    # WORLD
                    # ----------------------------------------

                    elif self.current_asset is not None:

                        tile_x, tile_y = (
                            self.get_tile_from_mouse(
                                mouse_x,
                                mouse_y
                            )
                        )

                        position = (
                            tile_x,
                            tile_y
                        )

                        old_asset = (
                            self.placed_assets.get(
                                position
                            )
                        )

                        # ------------------------------------
                        # PLAYER PLACEMENT
                        # ------------------------------------

                        if self.is_player_asset(
                            self.current_asset
                        ):

                            removed_players = {}

                            # Remove all existing players.
                            for player_position in (
                                self.get_player_positions()
                            ):

                                if player_position == position:
                                    continue

                                removed_players[
                                    player_position
                                ] = self.placed_assets[
                                    player_position
                                ]

                                self.placed_assets.pop(
                                    player_position
                                )

                            # If replacing a player at this tile,
                            # preserve the previous asset for undo.
                            action = Action(
                                position,
                                old_asset,
                                self.current_asset
                            )

                            # Store extra removed players so undo
                            # can restore them if necessary.
                            action.removed_players = (
                                removed_players
                            )

                            self.placed_assets[
                                position
                            ] = self.current_asset

                            self.undo_stack.append(action)

                            self.redo_stack.clear()

                            print(
                                "PLAYER SPAWN SET TO:",
                                position
                            )

                        # ------------------------------------
                        # NORMAL ASSET
                        # ------------------------------------

                        else:

                            action = Action(
                                position,
                                old_asset,
                                self.current_asset
                            )

                            self.placed_assets[
                                position
                            ] = self.current_asset

                            self.undo_stack.append(
                                action
                            )

                            self.redo_stack.clear()

                # --------------------------------------------
                # RIGHT CLICK = DELETE
                # --------------------------------------------

                elif event.button == 3:

                    tile_x, tile_y = (
                        self.get_tile_from_mouse(
                            mouse_x,
                            mouse_y
                        )
                    )

                    position = (
                        tile_x,
                        tile_y
                    )

                    if position in self.placed_assets:

                        old_asset = (
                            self.placed_assets[
                                position
                            ]
                        )

                        action = Action(
                            position,
                            old_asset,
                            None
                        )

                        self.placed_assets.pop(
                            position
                        )

                        self.undo_stack.append(
                            action
                        )

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

            world_x = int(x) * TILE_SIZE
            world_y = int(y) * TILE_SIZE

            screen_x, screen_y = (
                self.cam.world_to_screen(
                    world_x,
                    world_y
                )
            )

            screen_x = int(screen_x)
            screen_y = int(screen_y)

            image = self.get_asset_image(
                asset
            )

            if image is not None:

                screen.blit(
                    image,
                    (
                        screen_x,
                        screen_y
                    )
                )

        # --------------------------------------------------
        # UI
        # --------------------------------------------------

        self.pal.draw_palette(
            screen
        )

        mouse(screen)

        self.Box.draw(
            screen
        )

    # ======================================================
    # SAVE
    # ======================================================

    def save_level(self):

        print(
            "SAVING:",
            self.level_path
        )

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

        # Make absolutely sure only one
        # player is saved.
        self.clean_player_spawns()

        self.save_level()

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

        # Restore the asset that was originally
        # at the clicked position.
        if old_asset is None:

            self.placed_assets.pop(
                position,
                None
            )

        else:

            self.placed_assets[
                position
            ] = old_asset

        # Restore any player positions removed
        # by a player-reposition action.
        removed_players = getattr(
            action,
            "removed_players",
            {}
        )

        for player_position, player_asset in (
            removed_players.items()
        ):

            self.placed_assets[
                player_position
            ] = player_asset

        self.redo_stack.append(
            action
        )

    # ======================================================
    # REDO
    # ======================================================

    def redo(self):

        if not self.redo_stack:

            return

        action = self.redo_stack.pop()

        position = action.position
        new_asset = action.new_asset

        # Remove any players that were removed
        # during the original action.
        removed_players = getattr(
            action,
            "removed_players",
            {}
        )

        for player_position in (
            removed_players.keys()
        ):

            self.placed_assets.pop(
                player_position,
                None
            )

        if new_asset is None:

            self.placed_assets.pop(
                position,
                None
            )

        else:

            self.placed_assets[
                position
            ] = new_asset

        self.undo_stack.append(
            action
        )