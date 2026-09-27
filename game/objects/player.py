import pygame
from game.SpriteLoader import load_sprite_sheets

from ..systems.audio_manager import audio_manager

pygame.init()


class Player(pygame.sprite.Sprite):

    COLOR = (255, 0, 0)

    # --------------------------------------------------
    # PHYSICS
    # --------------------------------------------------

    GRAVITY = 0.65
    JUMP_STRENGTH = 11
    MAX_FALL_SPEED = 14

    # --------------------------------------------------
    # SPRITES
    # --------------------------------------------------

    SPRITES = load_sprite_sheets(
        "MainCharacters",
        "MaskDude",
        32,
        32,
        True
    )

    ANIMATION_DELAY = 3

    JUMP_SOUND = pygame.mixer.Sound(
        "game/SFX/sound1.mp3"
    )

    # --------------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------------

    def __init__(
        self,
        x,
        y,
        width,
        height
    ):

        super().__init__()

        self.rect = pygame.Rect(
            int(x),
            int(y),
            int(width),
            int(height)
        )

        self.x_vel = 0
        self.y_vel = 0

        self.mask = None

        self.direction = "right"

        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

        self.hit = False
        self.hit_count = 0

        # Prevent sprite access before first update.
        self.sprite = self.SPRITES[
            "idle_right"
        ][0]

        self.update()

    # ======================================================
    # JUMP
    # ======================================================

    def jump(self):

        # Maximum of two jumps.
        if self.jump_count >= 2:

            return False

        self.y_vel = -self.JUMP_STRENGTH

        self.animation_count = 0

        self.jump_count += 1

        # First jump resets falling timer.
        if self.jump_count == 1:

            self.fall_count = 0

            audio_manager.play_sfx(
                self.JUMP_SOUND
            )

        return True

    # ======================================================
    # BASIC MOVEMENT
    # ======================================================

    def move(
        self,
        dx,
        dy
    ):

        self.rect.x += int(dx)
        self.rect.y += int(dy)

    # ======================================================
    # RESPAWN
    # ======================================================

    def respawn(
        self,
        x,
        y
    ):

        self.rect.topleft = (
            int(x),
            int(y)
        )

        self.x_vel = 0
        self.y_vel = 0

        self.fall_count = 0
        self.jump_count = 0

        self.hit = False
        self.hit_count = 0

        self.animation_count = 0

    # ======================================================
    # HIT
    # ======================================================

    def make_hit(self):

        self.hit = True

    # ======================================================
    # LEFT
    # ======================================================

    def move_left(
        self,
        vel
    ):

        self.x_vel = -vel

        if self.direction != "left":

            self.direction = "left"

            self.animation_count = 0

    # ======================================================
    # RIGHT
    # ======================================================

    def move_right(
        self,
        vel
    ):

        self.x_vel = vel

        if self.direction != "right":

            self.direction = "right"

            self.animation_count = 0

    # ======================================================
    # PHYSICS LOOP
    # ======================================================

    def loop(
        self,
        fps
    ):

        # ----------------------------------------------
        # GRAVITY
        # ----------------------------------------------

        self.y_vel += self.GRAVITY

        if self.y_vel > self.MAX_FALL_SPEED:

            self.y_vel = self.MAX_FALL_SPEED

        # ----------------------------------------------
        # MOVEMENT
        # ----------------------------------------------

        self.move(
            self.x_vel,
            self.y_vel
        )

        # ----------------------------------------------
        # HIT STATE
        # ----------------------------------------------

        if self.hit:

            self.hit_count += 1

        if self.hit_count > fps * 2:

            self.hit = False
            self.hit_count = 0

        # ----------------------------------------------
        # FALL TIMER
        # ----------------------------------------------

        self.fall_count += 1

        # ----------------------------------------------
        # SPRITE
        # ----------------------------------------------

        self.update_sprite()

    # ======================================================
    # LAND
    # ======================================================

    def landed(self):

        self.fall_count = 0

        self.y_vel = 0

        self.jump_count = 0

    # ======================================================
    # HIT HEAD
    # ======================================================

    def hit_head(self):

        self.fall_count = 0

        # Stop upward movement immediately.
        if self.y_vel < 0:

            self.y_vel = 0

    # ======================================================
    # SPRITE UPDATE
    # ======================================================

    def update_sprite(self):

        sprite_sheet = "idle"

        # ----------------------------------------------
        # HIT
        # ----------------------------------------------

        if self.hit:

            sprite_sheet = "hit"

        # ----------------------------------------------
        # UPWARD
        # ----------------------------------------------

        elif self.y_vel < 0:

            if self.jump_count == 1:

                sprite_sheet = "jump"

            elif self.jump_count == 2:

                sprite_sheet = "double_jump"

        # ----------------------------------------------
        # FALLING
        # ----------------------------------------------

        elif self.y_vel > 2:

            sprite_sheet = "fall"

        # ----------------------------------------------
        # RUNNING
        # ----------------------------------------------

        elif self.x_vel != 0:

            sprite_sheet = "run"

        # ----------------------------------------------
        # GET DIRECTIONAL SPRITE
        # ----------------------------------------------

        sprite_sheet_name = (
            sprite_sheet
            + "_"
            + self.direction
        )

        # Safety fallback.
        if sprite_sheet_name not in self.SPRITES:

            sprite_sheet_name = (
                "idle_"
                + self.direction
            )

        sprites = self.SPRITES[
            sprite_sheet_name
        ]

        if not sprites:

            return

        sprite_index = (
            self.animation_count
            //
            self.ANIMATION_DELAY
        ) % len(sprites)

        self.sprite = sprites[
            sprite_index
        ]

        self.animation_count += 1

        self.update()

    # ======================================================
    # MASK
    # ======================================================

    def update(self):

        self.mask = pygame.mask.from_surface(
            self.sprite
        )

    # ======================================================
    # DRAW
    # ======================================================

    def draw(
        self,
        win,
        offset_x
    ):

        win.blit(
            self.sprite,
            (
                int(self.rect.x - offset_x),
                int(self.rect.y)
            )
        )