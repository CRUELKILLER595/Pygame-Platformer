
class SceneManager:
    def __init__(self,application=None):
        self.current_scene = None
        self.application = application


    def handle_events(self, events):
        self.current_scene.handle_events(events)

    def update(self):
        self.current_scene.update()

    def draw(self, screen):
        self.current_scene.draw(screen)
    def change_scene(self, scene):
     print("CHANGING TO:", type(scene).__name__)
     self.current_scene = scene

    def draw(self, screen):
     print("DRAWING:", type(self.current_scene).__name__)
     self.current_scene.draw(screen)
    def request_quit(self):
        if self.application:
            self.application.quit()