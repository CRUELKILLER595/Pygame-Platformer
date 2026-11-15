import pygame as p


class GameTimer:

    def __init__(self, time_limit):

        self.time_limit = float(time_limit)
        self.remaining = float(time_limit)

        self.running = False
        self.paused = False

        # Timestamp of the last timer update.
        self.last_update_ticks = None

    # ==========================================
    # START
    # ==========================================

    def start(self):

        self.running = True
        self.paused = False

        self.last_update_ticks = p.time.get_ticks()

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self):

        if not self.running or self.paused:
            return

        current_ticks = p.time.get_ticks()

        if self.last_update_ticks is None:
            self.last_update_ticks = current_ticks
            return

        elapsed_ms = current_ticks - self.last_update_ticks

        elapsed_seconds = max(
            0.0,
            elapsed_ms / 1000.0
        )

        self.remaining -= elapsed_seconds

        self.last_update_ticks = current_ticks

        if self.remaining <= 0:

            self.remaining = 0
            self.running = False
            self.last_update_ticks = None

    # ==========================================
    # PAUSE
    # ==========================================

    def pause(self):

        if not self.running:
            return

        # Account for elapsed time before pausing.
        self.update()

        self.running = False
        self.paused = True

        self.last_update_ticks = None

    # ==========================================
    # RESUME
    # ==========================================

    def resume(self):

        if not self.paused or self.remaining <= 0:
            return

        self.paused = False
        self.running = True

        # Start a fresh timing interval.
        self.last_update_ticks = p.time.get_ticks()

    # ==========================================
    # RESET
    # ==========================================

    def reset(self):

        self.remaining = self.time_limit

        self.running = False
        self.paused = False

        self.last_update_ticks = None

    # ==========================================
    # GET TIME
    # ==========================================

    def get_time(self):

        return int(max(0, self.remaining))