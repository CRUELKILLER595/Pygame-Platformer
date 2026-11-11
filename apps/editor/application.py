
import pygame

from pathlib import Path

from editor.config import (
    FPS,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)

from editor.runtime.scene_manager import EditorSceneManager

from editor.services.asset_library import EditorAssetLibrary

from pixelbound_core.assets.catalog_io import load_asset_catalog

from pixelbound_core.config.paths import CONTENT_DIR


class EditorApplication:

    def __init__(self, initial_scene=None):

        # ------------------------------------------
        # INITIALIZE PYGAME
        # ------------------------------------------

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        pygame.display.set_caption("PixelBound Editor")

        self.clock = pygame.time.Clock()

        self.running = True

        # ------------------------------------------
        # SCENE MANAGEMENT
        # ------------------------------------------

        self.scene_manager = EditorSceneManager()

        # ------------------------------------------
        # LOAD SHARED ASSET CATALOG
        # ------------------------------------------

        self.catalog_path = (
            CONTENT_DIR / "asset_catalog.json"
        )

        if not self.catalog_path.is_file():
            raise FileNotFoundError(
                f"Asset catalog not found: {self.catalog_path}. "
                "Run the catalog builder first."
            )

        self.asset_catalog = load_asset_catalog(
            self.catalog_path
        )

        # ------------------------------------------
        # INITIALIZE EDITOR ASSET LIBRARY
        # ------------------------------------------

        self.asset_library = EditorAssetLibrary(
            self.asset_catalog
        )

        self.assets = self.asset_library.load_assets()

        print("PIXELBOUND EDITOR INITIALIZED")
        print("Asset definitions:", len(self.asset_catalog))
        print("Loaded editor assets:", len(self.assets))

        # ------------------------------------------
        # INITIAL SCENE
        # ------------------------------------------

        if initial_scene is not None:
            self.scene_manager.change_scene(initial_scene)

    # ==========================================
    # APPLICATION LOOP
    # ==========================================

    def run(self):

        try:

            while self.running:

                events = pygame.event.get()

                for event in events:

                    if event.type == pygame.QUIT:
                        self.running = False

                if not self.running:
                    break

                self.scene_manager.handle_events(events)

                self.scene_manager.update()

                self.scene_manager.draw(self.screen)

                pygame.display.flip()

                self.clock.tick(FPS)

        finally:
            pygame.quit()

    # ==========================================
    # SHUTDOWN
    # ==========================================

    def quit(self):

        self.running = False
