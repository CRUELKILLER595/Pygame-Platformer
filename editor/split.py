from PIL import Image
import os


INPUT_IMAGE = "assets/Menu/Buttons/Sample.png"
OUTPUT_DIR = "assets/Menu/Buttons/split_buttons"

os.makedirs(OUTPUT_DIR, exist_ok=True)

sheet = Image.open(INPUT_IMAGE).convert("RGBA")


# --------------------------------------------------
# White buttons
# --------------------------------------------------

white_buttons = {
    "play_white_1":  (1, 1, 65, 33),
    "play_white_2":  (66, 4, 130, 33),

    "options_white_1": (142, 1, 238, 33),
    "options_white_2": (239, 4, 335, 33),

    "pause_white_1": (1, 34, 65, 66),
    "pause_white_2": (66, 37, 130, 66),

    "restart_white_1": (142, 34, 238, 66),
    "restart_white_2": (239, 37, 335, 66),

    "menu_white_1": (1, 67, 65, 99),
    "menu_white_2": (66, 70, 130, 99),

    "settings_white_1": (142, 67, 238, 99),
    "settings_white_2": (239, 70, 335, 99),

    "pause_icon_white_1": (1, 100, 33, 132),
    "pause_icon_white_2": (34, 102, 66, 132),

    "play_icon_white_1": (68, 100, 100, 132),
    "play_icon_white_2": (101, 102, 133, 132),
}


# --------------------------------------------------
# Blue buttons
# --------------------------------------------------

blue_buttons = {
    "play_blue_1":  (1, 144, 65, 176),
    "play_blue_2":  (66, 147, 130, 176),

    "options_blue_1": (142, 144, 238, 176),
    "options_blue_2": (239, 147, 335, 176),

    "pause_blue_1": (1, 177, 65, 209),
    "pause_blue_2": (66, 180, 130, 209),

    "restart_blue_1": (142, 177, 238, 209),
    "restart_blue_2": (239, 180, 335, 209),

    "menu_blue_1": (1, 210, 65, 242),
    "menu_blue_2": (66, 213, 130, 242),

    "settings_blue_1": (142, 210, 238, 242),
    "settings_blue_2": (239, 213, 335, 242),

    "pause_icon_blue_1": (1, 243, 33, 275),
    "pause_icon_blue_2": (34, 245, 66, 275),

    "play_icon_blue_1": (67, 243, 99, 275),
    "play_icon_blue_2": (100, 245, 132, 275),
}


def save_buttons(buttons):
    for name, rect in buttons.items():
        image = sheet.crop(rect)
        image.save(
            os.path.join(OUTPUT_DIR, f"{name}.png")
        )
        print("Saved:", name)


save_buttons(white_buttons)
save_buttons(blue_buttons)

print("Done.")