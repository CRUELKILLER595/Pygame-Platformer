import asyncio
import pygame as p

from .scenemanager import SceneManager
from .settings import FPS


class Application:

    def __init__(self, initial_scene_factory=None):

        p.init()

        self.width = 1250
        self.height = 900

        self.screen = p.display.set_mode(
            (self.width, self.height)
        )

        p.display.set_caption("PixelBound")

        self.clock = p.time.Clock()
        self.running = True

        # ------------------------------------------
        # FIXED TIMESTEP CONFIGURATION
        # ------------------------------------------

        self.fixed_dt = 1.0 / FPS
        self.accumulator = 0.0

        # Avoid excessive catch-up after browser stalls
        # or switching back to a suspended browser tab.
        self.max_frame_time = 0.1

        # ------------------------------------------
        # FPS DIAGNOSTICS
        # ------------------------------------------

        self.render_frames = 0
        self.simulation_steps = 0

        self.fps_start_time = p.time.get_ticks()

        # ------------------------------------------
        # SCENE MANAGER
        # ------------------------------------------

        self.scene_manager = SceneManager(self)

        if initial_scene_factory is None:

            from .scenes.menu_scene import MenuScene

            initial_scene_factory = MenuScene

        self.scene_manager.change_scene(
            initial_scene_factory(self.scene_manager)
        )

    # ==========================================
    # PROCESS ONE FRAME
    # ==========================================

    def process_frame(self):

        if not self.running:
            return False

        # ------------------------------------------
        # EVENTS
        # ------------------------------------------

        events = p.event.get()

        if any(event.type == p.QUIT for event in events):

            self.quit()
            return False

        self.scene_manager.handle_events(events)

        if not self.running:
            return False

        # ------------------------------------------
        # MEASURE FRAME TIME
        # ------------------------------------------

        frame_time = self.clock.tick(FPS) / 1000.0

        # Prevent a very long frame from causing
        # an excessive number of simulation updates.
        frame_time = min(
            frame_time,
            self.max_frame_time
        )

        self.accumulator += frame_time

        # ------------------------------------------
        # FIXED-RATE GAME SIMULATION
        # ------------------------------------------

        while self.accumulator >= self.fixed_dt:

            self.scene_manager.update()

            self.accumulator -= self.fixed_dt

            self.simulation_steps += 1

            if not self.running:
                return False

        # ------------------------------------------
        # RENDER
        # ------------------------------------------

        self.scene_manager.draw(self.screen)

        p.display.flip()

        # ------------------------------------------
        # PERFORMANCE DIAGNOSTICS
        # ------------------------------------------

        self.render_frames += 1

        current_time = p.time.get_ticks()

        elapsed = current_time - self.fps_start_time

        if elapsed >= 2000:

            render_fps = (
                self.render_frames * 1000.0 / elapsed
            )

            simulation_hz = (
                self.simulation_steps * 1000.0 / elapsed
            )

            print(
                f"RENDER FPS: {render_fps:.1f} | "
                f"SIMULATION HZ: {simulation_hz:.1f}"
            )

            self.render_frames = 0
            self.simulation_steps = 0

            self.fps_start_time = current_time

        return True

    # ==========================================
    # BROWSER GAME LOOP
    # ==========================================

    async def run_web(self):

        while self.running:

            if not self.process_frame():
                break

            await asyncio.sleep(0)

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