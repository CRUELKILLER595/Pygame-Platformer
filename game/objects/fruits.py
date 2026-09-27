from .collectible import Collectible


class Fruit(Collectible):

    VALUE = 100

    def __init__(self, x, y, image, fruit_type):
        super().__init__(
            x,
            y,
            image.get_width(),
            image.get_height(),
            image
        )

        self.fruit_type = fruit_type
        self.value = self.VALUE

    def collect(self, score_manager):

        if self.collected:
            return

        self.collected = True

        score_manager.collect_fruit()