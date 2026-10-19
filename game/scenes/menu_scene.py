import pygame as p
from ..scenemanager import SceneManager
from .base_scene import Scene
from ui.button import Button
from.level_select_scene import LevelSelectScene
from.AboutScene import AboutScene
from.level_editor_select_scene import EditorLevelSelectScene
from..systems.background import TiledBackground
from..settings import WIDTH, HEIGHT
from..systems.audio_manager import audio_manager
from .character_select_scene import CharacterSelectScene
from ui.auth import AuthPopup
import os
import pygame as p

from ui.button import Button
from ..systems.audio_manager import audio_manager
import os
Music_path=os.path.join("game","Music","MENU_MUSIC.wav")
p.init()
class MenuScene(Scene):
   
    def __init__(self, scene_manager):
    # Store scene manager
      self.scene_manager = scene_manager

    # Fonts — initialize these BEFORE creating buttons
      self.font = p.font.SysFont("Arial", 30)
      self.title_font = p.font.SysFont("Arial", 60)

    # Button asset paths
      Menu_Path = os.path.join(
        "assets", "Menu", "Buttons", "split_buttons"
    )
      Main_Path = os.path.join(
        "assets", "Menu", "Buttons"
    )

    # Load button images
      Play_button = p.image.load(
        os.path.join(Menu_Path, "Play.png")
    ).convert_alpha()

      Editor_button = p.image.load(
        os.path.join(Main_Path, "Editor.png")
    ).convert_alpha()

      Quit_button = p.image.load(
        os.path.join(Main_Path, "Close.png")
    ).convert_alpha()

    # Existing menu buttons
      self.play_button = Button(
        "Play",
        (500, 300),
        (250, 70),
        self.font,
        self.start_game,
        Play_button,
    )

      self.editor_button = Button(
        "EDITOR",
        (500, 375),
        (250, 70),
        self.font,
        self.start_editor,
        Editor_button,
    )

      self.about_button = Button(
        "ABOUT",
        (500, 450),
        (250, 70),
        self.font,
        self.start_about,
        None,
    )

      self.quit_button = Button(
        "Quit",
        (500, 525),
        (250, 70),
        self.font,
        self.quit_game,
        Quit_button,
    )

    # Login / Sign Up popup
      self.auth_popup = AuthPopup()

    # Login / Sign Up menu button
      self.auth_button = Button(
        "LOGIN / SIGN UP",
        (900, 525),
        (260, 70),
        self.font,
        self.open_auth,
        None,
    )

    # Start menu music
    audio_manager.play_music("menu")
    def start_game(self):
    
     print("PLAY CLICKED")
     self.scene_manager.change_scene(
        CharacterSelectScene(self.scene_manager)
    )
    def open_auth(self):
     self.auth_popup.show()
      

    def start_editor(self):

        print("EDITOR BUTTON PRESSED")
        self.scene_manager.change_scene(
            EditorLevelSelectScene(self.scene_manager)
        )

    def quit_game(self):
        p.mixer.music.stop()
        p.quit()
        raise SystemExit
    def start_about(self):
        print("ABOUT BUTTON PRESSED")
        self.scene_manager.change_scene(
            AboutScene(self.scene_manager)
        )
    def handle_events(self, events):

     for event in events:

        if event.type == p.QUIT:
            p.quit()
            raise SystemExit
        if self.auth_popup.visible:
            self.auth_popup.handle_event(event)
            continue
        self.auth_button.handle_event(event)
        self.play_button.handle_event(event)
        self.editor_button.handle_event(event)
        self.quit_button.handle_event(event)
        self.about_button.handle_event(event)
        return super().handle_events(events)
    def update(self):
        pass

    # ---------------------------------
    # DRAW
    # ---------------------------------

    def draw(self, screen):

        background = TiledBackground("assets/Background/Gray.png")
        background.draw(screen)

        title = self.title_font.render(
            "PIXELBOUND",
            True,
            (0, 0, 255)
        )

        title_rect = title.get_rect(
            center=(625, 150)
        )

        screen.blit(
            title,
            title_rect
        )
        
        self.play_button.draw(screen)
        self.editor_button.draw(screen)
        self.quit_button.draw(screen)
        self.about_button.draw(screen)
        self.auth_button.draw(screen)
        self.auth_popup.draw(screen)