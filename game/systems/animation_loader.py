import pygame as p
import os
from game.settings import TILE_SIZE
PATH="assets/Traps"
FRAME_SIZES = {
    "Fire": {
        "on": (16, 32),
        "off": (16, 32),
        "hit": (32, 32),
    },

    "Arrow": {
        "Idle": (18, 18),
        "Hit": (18, 18),
    },

    "Falling Platforms": {
        "On": (32, 10),
        "Off": (32, 10),
    },

    "Fan": {
        "On": (24, 8),
        "Off": (24, 8),
    },

    "Saw": {
        "on": (38, 38),
        "off": (38, 38)
        },
   
    
}
FRUIT_FRAME_SIZE=(32,32)

def extract_frames(image, frame_width, frame_height):

    frames = []

    for x in range(0, image.get_width(), frame_width):

        frame = image.subsurface(
            p.Rect(x, 0, frame_width, frame_height)
        ).copy()

        frame = p.transform.scale(
            frame,
            (TILE_SIZE, TILE_SIZE)
        )

        frames.append(frame)

    return frames
def load_animation_sheet(path, frame_width, frame_height):

    image = p.image.load(path).convert_alpha()

    return extract_frames(
        image,
        frame_width,
        frame_height
    )