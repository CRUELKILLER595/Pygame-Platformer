class ScoreManager:

    def __init__(self):
        self.score = 0
        self.fruits_collected = 0
        self.boxes_destroyed = 0
        self.deaths = 0

    def add_points(self, points):
        self.score += points

    def collect_fruit(self,value):
        self.fruits_collected += 1
        self.add_points(value)

    def destroy_box(self):
        self.boxes_destroyed += 1
        self.add_points(50)

    def player_died(self):
        self.deaths += 1
        self.add_points(-100)