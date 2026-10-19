from ..settings import PLAYER_VEL


CHARACTERS = {
    "mask_dude": {
        "display_name": "Mask Dude",
        "sprite_folder": "MaskDude",

        "frame_width": 32,
        "frame_height": 32,
        "animation_delay": 3,

        "move_speed": PLAYER_VEL,
        "gravity": 0.65,
        "jump_strength": 11,
        "max_fall_speed": 14,
    },

    "ninja_frog": {
        "display_name": "Ninja Frog",
        "sprite_folder": "NinjaFrog",

        "frame_width": 32,
        "frame_height": 32,
        "animation_delay": 3,

        "move_speed": PLAYER_VEL,
        "gravity": 0.65,
        "jump_strength": 11,
        "max_fall_speed": 14,
    },

    "pink_man": {
        "display_name": "Pink Man",
        "sprite_folder": "PinkMan",

        "frame_width": 32,
        "frame_height": 32,
        "animation_delay": 3,

        "move_speed": PLAYER_VEL,
        "gravity": 0.65,
        "jump_strength": 11,
        "max_fall_speed": 14,
    },

    "virtual_guy": {
        "display_name": "Virtual Guy",
        "sprite_folder": "VirtualGuy",

        "frame_width": 32,
        "frame_height": 32,
        "animation_delay": 3,

        "move_speed": PLAYER_VEL,
        "gravity": 0.65,
        "jump_strength": 11,
        "max_fall_speed": 14,
    },
}


DEFAULT_CHARACTER = "mask_dude"