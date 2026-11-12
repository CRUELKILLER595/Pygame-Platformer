
import pygame as p

from .scenemanager import SceneManager


class Application:

    def __init__(self):

        # Initialize Pygame
        p.init()

        self.width = 1250
        self.height = 900

        self.screen = p.display.set_mode(
            (self.width, self.height)
        )

        p.display.set_caption("PixelBound")

        self.clock = p.time.Clock()
        self.running = True

        # Initialize Scene Manager
        self.scene_manager = SceneManager(self)

        # Import scenes after Pygame initialization
        from .scenes.menu_scene import MenuScene

        self.scene_manager.change_scene(
            MenuScene(self.scene_manager)
        )

    # ==========================================
    # PROCESS ONE FRAME
    # ==========================================

    def process_frame(self):

        if not self.running:
            return False

        events = p.event.get()

        # Application owns window shutdown
        if any(event.type == p.QUIT for event in events):
            self.quit()
            return False

        # Process scene events
        self.scene_manager.handle_events(events)

        if not self.running:
            return False

        # Update
        self.scene_manager.update()

        # Render
        self.scene_manager.draw(self.screen)

        p.display.flip()

        return True

    # ==========================================
    # DESKTOP GAME LOOP
    # ==========================================

    def run(self):

        try:
            while self.running:
                self.process_frame()

        finally:
            p.quit()

    # ==========================================
    # SHUTDOWN
    # ==========================================

    def quit(self):

        self.running = False
