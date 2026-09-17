import pygame as p
from ..scenemanager import SceneManager
from .base_scene import Scene
from ui.button import Button
from.level_select_scene import LevelSelectScene
from.EditorScene import EditorScene
from.level_editor_select_scene import EditorLevelSelectScene
import os
Music_path=os.path.join("game","Music","MENU_MUSIC.wav")
p.init()
class MenuScene(Scene):
    def play_music(self):
     p.mixer.music.load(Music_path)
     p.mixer.music.play(-1)
    def __init__(self, scene_manager):
        Menu_Path=os.path.join("assets", "Menu","Buttons", "split_buttons")
        Main_Path=os.path.join("assets", "Menu","Buttons")
        Play_button=p.image.load(os.path.join(Menu_Path, "Play.png")).convert_alpha()
        Editor_button=p.image.load(os.path.join(Main_Path, "Editor.png")).convert_alpha()
        Quit_button=p.image.load(os.path.join(Main_Path, "Close.png")).convert_alpha()
        self.scene_manager=scene_manager
        self.font=p.font.SysFont("Arial", 30)
        self.title_font=p.font.SysFont("Arial", 60)
        self.play_button=Button("Play", (500,300),(250,70), self.font, self.start_game,Play_button)
        self.quit_button=Button("Quit", (500,600),(250,70), self.font, self.quit_game,Quit_button)
        self.editor_button = Button( "EDITOR", (500, 450),(250,70),self.font, self.start_editor,Editor_button)
        self.play_music()
    def start_game(self):
    
     print("PLAY CLICKED")
     self.scene_manager.change_scene(
        LevelSelectScene(self.scene_manager)
    )
      

    def start_editor(self):

        print("EDITOR BUTTON PRESSED")
        self.scene_manager.change_scene(
            EditorLevelSelectScene(self.scene_manager)
        )
        p.mixer.music.stop()

    def quit_game(self):
        p.mixer.music.stop()
        p.quit()
        raise SystemExit
    def handle_events(self, events):

     for event in events:

        if event.type == p.QUIT:
            p.quit()
            raise SystemExit

        self.play_button.handle_event(event)
        self.editor_button.handle_event(event)
        self.quit_button.handle_event(event)
        return super().handle_events(events)
    def update(self):
        pass

    # ---------------------------------
    # DRAW
    # ---------------------------------

    def draw(self, screen):

        screen.fill((20, 20, 20))

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
    