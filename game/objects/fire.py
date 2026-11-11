from .trap import Trap


class Fire(Trap):

    def __init__(
        self,
        x,
        y,
        width,
        height,
        animations=None,
        name="Fire",
        image=None,
        collision_profile=None,
        animation_speed=4,
        asset=None,
    ):
        if asset is not None:
            animations = getattr(
                asset,
                "animations",
                animations
            )

            name = getattr(
                asset,
                "name",
                "Fire"
            )

            image = getattr(
                asset,
                "image",
                image
            )

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            animations=animations,
            name=name or "Fire",
            image=image,
            collision_profile=collision_profile,
            animation_speed=animation_speed,
        )

    def on(self):
        self.set_animation("on")

    def off(self):
        self.set_animation("off")
