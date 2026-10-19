from .object import Object


class End(Object):

    def __init__(
        self,
        x,
        y,
        idle_image,
        pressed_image
    ):

        super().__init__(
            x,
            y,
            idle_image.get_width(),
            idle_image.get_height(),
            "end"
        )

        self.idle_image = idle_image
        self.pressed_image = pressed_image

        self.image = self.idle_image
        self.completed = False
    def check_collision(self, player):

        if self.completed:
            return False

        if self.rect.colliderect(player.rect):

            self.complete()
            return True

        return False

    def complete(self):

        self.completed = True
        self.image = self.pressed_image

    def reset(self):

        self.completed = False
        self.image = self.idle_image