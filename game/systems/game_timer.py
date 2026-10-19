import pygame as p
from game.settings import FPS

class GameTimer:

    def __init__(self, time_limit):

        self.time_limit = time_limit
        self.remaining = float(time_limit)

        self.running = False
        self.paused = False

    def start(self):

        self.running = True
        self.paused = False

    def update(self):

        if not self.running or self.paused:
            return

        self.remaining -= 1 / 300

        if self.remaining <= 0:

            self.remaining = 0
            self.running = False

    def pause(self):

        self.paused = True
        self.running=False

    def resume(self):

        self.paused = False

    def reset(self):

        self.remaining = float(
            self.time_limit
        )
        self.running = False
        self.paused = False

    def get_time(self):

        return int(
            self.remaining
        )