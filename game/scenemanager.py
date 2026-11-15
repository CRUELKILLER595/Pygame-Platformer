
class SceneManager:
    def __init__(self,application=None):
        self.current_scene = None
        self.application = application


    def handle_events(self, events):
        self.current_scene.handle_events(events)

    def update(self):
        self.current_scene.update()

   
    def change_scene(self, scene):

     if isinstance(scene, type):
        raise TypeError(
            f"Expected a scene instance, received "
            f"{scene.__name__}. Pass {scene.__name__}(...) instead."
        )

     print("CHANGING TO:", type(scene).__name__)
     self.current_scene = scene
       

    def draw(self, screen):
        if self.current_scene is not None:
            self.current_scene.draw(screen)

    def request_quit(self):
        if self.application:
            self.application.quit()