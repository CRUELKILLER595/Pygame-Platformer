

import sys
import pygame

from apps.editor.application import EditorApplication
from editor.scenes.level_select_scene import EditorLevelSelectScene
from editor.scenes.editor_scene import EditorScene
from pixelbound_core.config.paths import LEVELS_DIR


def main():

    application = EditorApplication()

    # Start at the Level Selector.
    selector = EditorLevelSelectScene(application)
    application.scene_manager.change_scene(selector)

    print("\nLEVEL NAVIGATION TEST")
    print("-" * 45)

    print(
        "Initial scene:",
        type(application.scene_manager.current_scene).__name__
    )

    # Select Level 1.
    selector.select_level(LEVELS_DIR / "level1.json")

    active_scene = application.scene_manager.current_scene

    print("Active scene:", type(active_scene).__name__)
    print("Loaded level:", active_scene.level_path.name)
    print("Placed objects:", len(active_scene.placed_assets))

    assert isinstance(active_scene, EditorScene)
    assert active_scene.level_path.name == "level1.json"
    assert len(active_scene.placed_assets) == 70

    game_imports = [
        name
        for name in sys.modules
        if name == "game" or name.startswith("game.")
    ]

    assert not game_imports, game_imports

    print("[PASS] Level Selector -> EditorScene")
    print("[PASS] Level data loaded")
    print("[PASS] Game independence")

    pygame.quit()


if __name__ == "__main__":
    main()
