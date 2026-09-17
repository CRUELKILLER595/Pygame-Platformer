import pygame as p
p.init()
class SceneManager:
    def __init__(self):
        self.current_scene = None


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