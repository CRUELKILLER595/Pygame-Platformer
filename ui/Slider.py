import pygame as p
class Slider:

    def __init__(self, x, y, width, value=1.0):

        self.x = x
        self.y = y
        self.width = width
        self.value = value

        self.dragging = False

        self.rect = p.Rect(
            x,
            y,
            width,
            10
        )

    def handle_event(self, event):

        if event.type == p.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == p.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == p.MOUSEMOTION:

            if self.dragging:
                self.value = (
                    event.pos[0] - self.x
                ) / self.width

                self.value = max(
                    0.0,
                    min(1.0, self.value)
                )

    def draw(self, screen):

        p.draw.rect(
            screen,
            (80, 80, 80),
            self.rect
        )

        knob_x = self.x + int(
            self.value * self.width
        )

        p.draw.circle(
            screen,
            (0, 120, 255),
            (knob_x, self.y + 5),
            8
        )