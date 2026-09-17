import pygame as py

from .json_manager import save_level, load_level
from game.settings import FPS, TILE_SIZE, SPRITE_SIZE, screen_width
from .Grid import draw_grid
from .mouse import mouse
from .camera import camera
from .asset_library import load_assets
from .palette import Palette
from .dropdown import OptionBox
from .undo_redo import Action


# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

py.init()

screen_height = 800
lower_margin = 100
side_margin = 300

camera_speed = 10

level_data = {
    "version": 1,
    "level_name": "Level1",
    "objects": []
}

undo_stack = []
redo_stack = []

option_list = ["CHARACTERS", "TILES"]

font = py.font.SysFont("TimesNewRoman", 24)

screen = py.display.set_mode(
    (screen_width + side_margin, screen_height + lower_margin)
)

py.display.set_caption("LEVEL EDITOR")

clock = py.time.Clock()

# Camera controls only the world area
cam = camera(screen_width, screen_height)

# Load all available assets
ASSETS = load_assets()

# Load existing level
placed_assets = load_level(ASSETS)

# Current selected asset from palette
current_asset = None

# Palette
pal = Palette(
    ASSETS,
    screen_width + 10,
    55,
    300,
    "Characters"
)

# Dropdown
Box = OptionBox(
    screen_width + 40,
    0,
    200,
    50,
    (255, 255, 255),
    font,
    option_list
)


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

def main(screen):

    running = True

    while running:

        clock.tick(FPS)

        # ==========================================
        # 1. INPUT
        # ==========================================

        event_list = py.event.get()
        keys = py.key.get_pressed()

        mouse_x, mouse_y = py.mouse.get_pos()

        # ------------------------------------------
        # Dropdown
        # ------------------------------------------

        selected = Box.update(event_list)

        if selected != -1:
            pal.category = selected

        # ------------------------------------------
        # Events
        # ------------------------------------------

        for event in event_list:

            # --------------------------------------
            # QUIT
            # --------------------------------------

            if event.type == py.QUIT:
                running = False

            # --------------------------------------
            # LEFT CLICK
            # --------------------------------------

            elif event.type == py.MOUSEBUTTONDOWN:

                if event.button == 1:

                    # ==============================
                    # PALETTE
                    # ==============================

                    if mouse_x >= screen_width:

                        clicked_asset = pal.get_clicked_asset(
                            (mouse_x, mouse_y)
                        )

                        if clicked_asset is not None:
                            current_asset = clicked_asset

                            print(
                                "Selected:",
                                current_asset.id
                            )

                    # ==============================
                    # WORLD
                    # ==============================

                    elif current_asset is not None:

                        # Screen → World
                        world_x, world_y = cam.screen_to_world(
                            mouse_x,
                            mouse_y
                        )

                        # World → Grid
                        tile_x = world_x // TILE_SIZE
                        tile_y = world_y // TILE_SIZE

                        print(
                            "Placing",
                            current_asset.id,
                            "AT",
                            tile_x,
                            tile_y
                        )

                        # Check if something already exists
                        old_asset = placed_assets.get(
                            (tile_x, tile_y)
                        )

                        # Create action
                        action = Action(
                            (tile_x, tile_y),
                            old_asset,
                            current_asset
                        )

                        # Place / replace asset
                        placed_assets[
                            (tile_x, tile_y)
                        ] = current_asset

                        # Add to undo
                        undo_stack.append(action)

                        # New action destroys redo history
                        redo_stack.clear()

                # ----------------------------------
                # RIGHT CLICK
                # ----------------------------------

                elif event.button == 3:

                    world_x, world_y = cam.screen_to_world(
                        mouse_x,
                        mouse_y
                    )

                    tile_x = world_x // TILE_SIZE
                    tile_y = world_y // TILE_SIZE

                    position = (tile_x, tile_y)

                    if position not in placed_assets:
                        continue

                    old_asset = placed_assets.get(position)

                    action = Action(
                        position,
                        old_asset,
                        None
                    )

                    placed_assets.pop(position)

                    undo_stack.append(action)

                    redo_stack.clear()

            # --------------------------------------
            # KEYBOARD
            # --------------------------------------

            elif event.type == py.KEYDOWN:

                # ==============================
                # SAVE
                # ==============================

                if event.key == py.K_s:

                    save_level(
                        level_data,
                        placed_assets
                    )

                # ==============================
                # UNDO
                # CTRL + Z
                # ==============================

                elif (
                    event.key == py.K_z
                    and py.key.get_mods() & py.KMOD_CTRL
                ):

                    if undo_stack:

                        action = undo_stack.pop()

                        position = action.position
                        old_asset = action.old_asset

                        if old_asset is None:

                            placed_assets.pop(
                                position,
                                None
                            )

                        else:

                            placed_assets[
                                position
                            ] = old_asset

                        redo_stack.append(action)

                # ==============================
                # REDO
                # CTRL + Y
                # ==============================

                elif (
                    event.key == py.K_y
                    and py.key.get_mods() & py.KMOD_CTRL
                ):

                    if redo_stack:

                        action = redo_stack.pop()

                        position = action.position
                        new_asset = action.new_asset

                        if new_asset is None:

                            placed_assets.pop(
                                position,
                                None
                            )

                        else:

                            placed_assets[
                                position
                            ] = new_asset

                        undo_stack.append(action)

        # ==========================================
        # 2. CAMERA
        # ==========================================

        if keys[py.K_LEFT]:
            cam.x -= camera_speed

        elif keys[py.K_RIGHT]:
            cam.x += camera_speed

        if keys[py.K_UP]:
            cam.y -= camera_speed

        elif keys[py.K_DOWN]:
            cam.y += camera_speed

        # ==========================================
        # 3. MOUSE → WORLD
        # ==========================================

        world_x, world_y = cam.screen_to_world(
            mouse_x,
            mouse_y
        )

        tile_x = world_x // TILE_SIZE
        tile_y = world_y // TILE_SIZE

        # ==========================================
        # 4. RENDER WORLD
        # ==========================================

        screen.fill((1, 0, 0))

        # Infinite/procedural grid
        draw_grid(
            screen,
            cam
        )

        # ------------------------------------------
        # Draw placed assets
        # ------------------------------------------

        for (x, y), asset in placed_assets.items():

            # Grid → World
            world_x = x * TILE_SIZE
            world_y = y * TILE_SIZE

            # World → Screen
            screen_x, screen_y = cam.world_to_screen(
                world_x,
                world_y
            )

            screen.blit(
                asset.image,
                (screen_x, screen_y)
            )

        # ==========================================
        # 5. RENDER EDITOR UI
        # ==========================================

        # Palette is screen-space UI.
        # Camera does NOT affect it.
        pal.draw_palette(screen)

        mouse(screen)

        Box.draw(screen)

        # ==========================================
        # DISPLAY
        # ==========================================

        py.display.flip()

    py.quit()


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main(screen)