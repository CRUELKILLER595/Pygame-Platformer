
import sys
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

    print("\nEDITOR SCENE TEST")
    print("-" * 45)

    print("Scene:", type(scene).__name__)
    print("Level:", scene.level_path.name)
    print("Assets:", len(scene.ASSETS))
    print("Placed objects:", len(scene.placed_assets))
    print("Categories:", scene.option_list)

    game_imports = [
        module
        for module in sys.modules
        if module == "game" or module.startswith("game.")
    ]

    print("Game imports:", game_imports)

    assert len(scene.ASSETS) == 298
    assert len(scene.placed_assets) == 70
    assert not game_imports

    print("\nEDITOR SCENE FOUNDATION PASSED")

    pygame.quit()


if __name__ == "__main__":
    main()
