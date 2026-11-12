import pygame as p
from .scenemanager import SceneManager
class Application:

     def __init__(self):
      p.init()

      self.width = 1250
      self.height = 900

      self.screen = p.display.set_mode(
        (self.width, self.height)
    )

      p.display.set_caption("PixelBound")

      self.clock = p.time.Clock()
      self.running = True

    # Import scenes only after Pygame initialization.
      from.scenes.menu_scene import MenuScene

      self.scene_manager = SceneManager()
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