
from apps.editor.application import EditorApplication

from editor.scenes.level_select_scene import EditorLevelSelectScene


def main():

    application = EditorApplication()

    level_selector = EditorLevelSelectScene(
        application
    )

    application.scene_manager.change_scene(
        level_selector
    )

    application.run()


if __name__ == "__main__":
    main()
