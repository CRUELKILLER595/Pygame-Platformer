from .object import Object


class AnimatedObject(Object):

    ANIMATION_DELAY = 3

    def __init__(
        self,
        x,
        y,
        width,
        height,
        name,
        animations,
        default_animation="idle"
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            name
        )

        self.animations = animations
        self.animation_name = default_animation
        self.animation_count = 0

        self.image = self.animations[
            self.animation_name
        ][0]

    def play(self, animation_name):

        if animation_name not in self.animations:
            return

        if self.animation_name != animation_name:
            self.animation_name = animation_name
            self.animation_count = 0

    def loop(self):

        sprites = self.animations[self.animation_name]

        sprite_index = (
            self.animation_count // self.ANIMATION_DELAY
        ) % len(sprites)

        self.image = sprites[sprite_index]

        self.animation_count += 1

        self.rect = self.image.get_rect(
            topleft=self.rect.topleft
        )

        if (
            self.animation_count
            // self.ANIMATION_DELAY
            >= len(sprites)
        ):
            self.animation_count = 0
            