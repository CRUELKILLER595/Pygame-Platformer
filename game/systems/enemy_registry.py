# game/systems/enemy_registry.py

# Default enemy ID for future gameplay configuration.
DEFAULT_ENEMY = "enemy_bee_black"


def sprite_sheet(filename, frame_size):
    return {
        "file": filename,
        "frame_size": frame_size
    }


# --------------------------------------------------
# ENEMY REGISTRY
# --------------------------------------------------

ENEMY_REGISTRY = {

    # ==============================================
    # BEES
    # ==============================================

    "enemy_bee_black": {
        "name": "Black Bee",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Bee_Black.png",
                (16, 16)
            ),
            "death": sprite_sheet(
                "Bee_Black_ko.png",
                (16, 16)
            ),
            "bones": sprite_sheet(
                "Bee_bones.png",
                (16, 16)
            ),
            "explosion": sprite_sheet(
                "Bee_Exp.png",
                (16, 16)
            )
        }
    },

    "enemy_bee_blue": {
        "name": "Blue Bee",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Bee_Blue.png",
                (16, 16)
            ),
            "death": sprite_sheet(
                "Bee_Blue_ko.png",
                (16, 16)
            ),
            "bones": sprite_sheet(
                "Bee_bones.png",
                (16, 16)
            ),
            "explosion": sprite_sheet(
                "Bee_Exp.png",
                (16, 16)
            )
        }
    },

    # ==============================================
    # FROGS
    # ==============================================

    "enemy_frog_green": {
        "name": "Green Frog",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Fro_Green.png",
                (16, 16)
            )
        }
    },

    "enemy_frog_orange": {
        "name": "Orange Frog",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Fro_Orange.png",
                (16, 16)
            )
        }
    },

    "enemy_frog_red": {
        "name": "Red Frog",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Fro_red.png",
                (16, 16)
            )
        }
    },

    # ==============================================
    # SHEEP
    # ==============================================

    "enemy_sheep_blue": {
        "name": "Blue Sheep",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "She_Blue.png",
                (16, 16)
            )
        }
    },

    "enemy_sheep_green": {
        "name": "Green Sheep",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "She_green.png",
                (16, 16)
            )
        }
    },

    "enemy_sheep_red": {
        "name": "Red Sheep",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "She_red.png",
                (16, 16)
            )
        }
    },

    "enemy_sheep_yellow": {
        "name": "Yellow Sheep",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "She_Yellow.png",
                (16, 16)
            )
        }
    },

    # ==============================================
    # TURTLES
    # ==============================================

    "enemy_turtle_blue": {
        "name": "Blue Turtle",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Tur_Blue.png",
                (20, 32)
            ),
            "death": sprite_sheet(
                "Tur_Bones.png",
                (20, 32)
            ),
            "front": sprite_sheet(
                "Tur_front.png",
                (20, 32)
            )
        }
    },

    "enemy_turtle_green": {
        "name": "Green Turtle",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Tur_green.png",
                (20, 32)
            ),
            "death": sprite_sheet(
                "Tur_Bones.png",
                (20, 32)
            ),
            "front": sprite_sheet(
                "Tur_front.png",
                (20, 32)
            ),
            "back": sprite_sheet(
                "Tur_Green_back.png",
                (20, 32)
            ),
            "side": sprite_sheet(
                "Tur_Green_Side.png",
                (20, 32)
            )
        }
    },

    "enemy_turtle_red": {
        "name": "Red Turtle",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Tur_red.png",
                (20, 32)
            ),
            "death": sprite_sheet(
                "Tur_Bones.png",
                (20, 32)
            ),
            "front": sprite_sheet(
                "Tur_front.png",
                (20, 32)
            ),
            "back": sprite_sheet(
                "Tur_red_back.png",
                (20, 32)
            )
        }
    },

    "enemy_turtle_yellow": {
        "name": "Yellow Turtle",
        "lethal": True,
        "animations": {
            "idle": sprite_sheet(
                "Tur_Yellow.png",
                (20, 32)
            ),
            "death": sprite_sheet(
                "Tur_Bones.png",
                (20, 32)
            ),
            "front": sprite_sheet(
                "Tur_front.png",
                (20, 32)
            ),
            "back": sprite_sheet(
                "Tur_Yellow_back.png",
                (20, 32)
            )
        }
    }
}


# --------------------------------------------------
# REGISTRY HELPERS
# --------------------------------------------------

def get_enemy_definition(enemy_id):
    return ENEMY_REGISTRY.get(enemy_id)


def get_enemy_ids():
    return tuple(ENEMY_REGISTRY.keys())


def get_enemy_names():
    return {
        enemy_id: definition["name"]
        for enemy_id, definition
        in ENEMY_REGISTRY.items()
    }