import json

def save_level(level_data, placed_assets):
    print("SAVE..")

    level_data["objects"] = []

    for (x, y), asset in placed_assets.items():
        object_data = {
            "id": asset.id,
            "x": x,
            "y": y
        }

        level_data["objects"].append(object_data)

    with open("levels/level1.json", "w") as file:
        json.dump(level_data, file, indent=4)

    print("File saved successfully")
def load_level(ASSETS):
 placed_assets={}
 with open("levels/level1.json", "r") as file:
    level_data = json.load(file)
    for object in level_data["objects"]:
       asset_id = object["id"]
       x = object["x"]
       y = object["y"]
       asset = ASSETS[asset_id]
       placed_assets[(x,y)]=asset
    return placed_assets

