
class EditorSceneManager:
    """Manage scenes belonging exclusively to PixelBound Editor."""

    def __init__(self):
        self.current_scene = None

    def change_scene(self, scene):
        self.current_scene = scene
        print("EDITOR: Switching to", type(scene).__name__)

    def handle_events(self, events):
        if self.current_scene is not None:
            self.current_scene.handle_events(events)

    def update(self):
        if self.current_scene is not None:
            self.current_scene.update()

    def draw(self, screen):
        if self.current_scene is not None:
            self.current_scene.draw(screen)
        else:
            screen.fill((25, 25, 30))
