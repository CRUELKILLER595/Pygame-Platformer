class ScoreManager:

    FRUIT_TYPES = (
        "Apple",
        "Bananas",
        "Cherries",
        "Kiwi",
        "Melon",
        "Orange",
        "Pineapple",
        "Strawberry",
    )

    def __init__(self):
        self.score = 0
        self.fruits_collected = 0
        self.boxes_destroyed = 0
        self.deaths = 0

        # Track each fruit type independently.
        self.fruit_counts = {
            fruit: 0 for fruit in self.FRUIT_TYPES
        }

    def add_points(self, points):
        self.score += points

    def collect_fruit(self, value, fruit_type=None):
        self.fruits_collected += 1
        self.add_points(value)

        # Keep the per-fruit count.
        if fruit_type:
            fruit_name = next(
                (
                    name for name in self.fruit_counts
                    if name.casefold() == str(fruit_type).strip().casefold()
                ),
                None
            )

            if fruit_name is not None:
                self.fruit_counts[fruit_name] += 1

    def destroy_box(self):
        self.boxes_destroyed += 1
        self.add_points(50)

    def player_died(self):
        self.deaths += 1
        self.add_points(-100)