import pygame as p
from .scenemanager import SceneManager
from.scenes.menu_scene import MenuScene
class Application:

     def __init__(self):

        p.init()

        self.width = 1250
        self.height = 900

        self.screen = p.display.set_mode(
            (self.width, self.height)
        )

        p.display.set_caption("Platformer")

        self.clock = p.time.Clock()

        self.running = True

        # Create scene manager
        self.scene_manager = SceneManager()

        # IMPORTANT:
        # Set the first scene
        self.scene_manager.change_scene(
            MenuScene(self.scene_manager)
        )
     def run(self):
        while self.running:

            events = p.event.get()

            self.scene_manager.handle_events(events)
            self.scene_manager.update()
            self.scene_manager.draw(self.screen)

            p.display.flip()