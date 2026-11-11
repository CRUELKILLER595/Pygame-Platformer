
import pygame

from apps.editor.application import EditorApplication
from editor.scenes.editor_scene import EditorScene
from pixelbound_core.config.paths import LEVELS_DIR


def main():

    application = EditorApplication()

    scene = EditorScene(
        application,
        LEVELS_DIR / "level1.json"
    )

    surface = pygame.Surface((1300, 900))

    # Test rendering.
    scene.draw(surface)
    print("[PASS] World rendering")

    original_count = len(scene.placed_assets)

    # Choose a non-player asset.
    test_assets = (
    scene.ASSETS.values()
    if isinstance(scene.ASSETS, dict)
    else scene.ASSETS
)

    test_asset = next(
    (
        asset
        for asset in test_assets
        if asset.role != "player_spawn"
        and asset.image is not None
    ),
    None
)

    assert test_asset is not None, "No suitable test asset found."

    # Find a free grid position.
    test_position = None

    for y in range(100):
        for x in range(100):
            if (x, y) not in scene.placed_assets:
                test_position = (x, y)
                break
        if test_position is not None:
            break

    assert test_position is not None

    # Convert the selected world tile to a screen click.
    world_x = test_position[0] * 52 + 10
    world_y = test_position[1] * 52 + 10

    screen_x, screen_y = scene.cam.world_to_screen(
        world_x,
        world_y
    )

    scene.current_asset = test_asset

    # Simulate left click placement.
    placement_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "pos": (int(screen_x), int(screen_y)),
            "button": 1
        }
    )

    scene.handle_events([placement_event])

    surface = pygame.Surface((1300, 900))

    

    surface.fill((1, 2, 3))
    before_render = pygame.image.tostring(surface, "RGB")

    scene.draw(surface)

    after_render = pygame.image.tostring(surface, "RGB")

    assert before_render != after_render

    print("[PASS] Actual world rendering")
    


if __name__ == "__main__":
    main()
