from .animated_object import AnimatedObject


class Fruit(AnimatedObject):

    VALUE = 100

    def __init__(self, x, y, asset, fruit_type):

        super().__init__(
            x,
            y,
            asset.width,
            asset.height,
            asset.name,
            asset.animations,
            "idle"
        )

        self.fruit_type = fruit_type
        self.collected = False
        self.value = asset.score_value

    def collect(self, score_manager):

        if self.collected:
            return

        self.collected = True
        score_manager.collect_fruit(self.value)
