
"""Shared collision geometry helpers."""

DEBUG_HITBOXES = False


def make_collision_rect(sprite_rect, ratios):
    """
    Build a collision rectangle relative to a sprite rectangle.

    ratios: (x_offset, y_offset, width_ratio, height_ratio)
    """

    rx, ry, rw, rh = ratios

    left = sprite_rect.left + round(sprite_rect.width * rx)
    top = sprite_rect.top + round(sprite_rect.height * ry)

    width = max(1, round(sprite_rect.width * rw))
    height = max(1, round(sprite_rect.height * rh))

    return sprite_rect.__class__(
        left,
        top,
        width,
        height
    )
