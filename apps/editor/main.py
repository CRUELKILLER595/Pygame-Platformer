
from apps.editor.application import EditorApplication
from editor.scenes.title_scene import EditorTitleScene


def main():

    application = EditorApplication()

    title_scene = EditorTitleScene(application)

    application.scene_manager.change_scene(
        title_scene
    )

    application.run()


if __name__ == "__main__":
    main()
