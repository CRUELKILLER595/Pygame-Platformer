import pygame as p
p.init()
class MenuScene:
    def __init__(self):
        self.font = p.font.Font(None, 36)
        self.title_text = self.font.render("Platformer Game", True, (255, 255, 255))
        self.start_text = self.font.render("Press Enter to Start", True, (255, 255, 255))

    def handle_events(self, events):
        for event in events:
            if event.type == p.KEYDOWN and event.key == p.K_RETURN:
                return "game"  # Switch to the game scene
        return None

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))  # Clear the screen with black
        screen.blit(self.title_text, (screen.get_width() // 2 - self.title_text.get_width() // 2, 100))
        screen.blit(self.start_text, (screen.get_width() // 2 - self.start_text.get_width() // 2, 200))