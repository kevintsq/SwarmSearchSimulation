import os
import sqlite3


class Logger:
    def __init__(self, robot_max_cnt=10, reset=False):
        attributes = {"no": "INT",
                      "site_width": "INT",
                      "site_height": "INT",
                      "room_cnt": "INT",
                      "injury_cnt": "INT",
                      "departure_position": "TEXT",
                      "robot_type": "TEXT",
                      "robot_cnt": "INT",
                      "mode": "TEXT",
                      "room_visited": "INT",
                      "injury_rescued": "INT",
                      "returned": "INT",
                      "total_action_cnt": "INT"}
        for i in range(robot_max_cnt):
            attributes[f"robot_{i}_visits"] = "INT"
            attributes[f"robot_{i}_rescues"] = "INT"
            attributes[f"robot_{i}_collides"] = "INT"
        self.attributes = tuple(attributes.keys())
        if not os.path.exists("results"):
            os.mkdir("results")
        is_exist = os.path.exists("results/results.db")
        if reset and is_exist:
            os.remove("results/results.db")
        self.db = sqlite3.connect("results/results.db")
        self.cursor = self.db.cursor()
        if reset or not is_exist:
            self.cursor.execute(
                    f"CREATE TABLE results ({','.join((' '.join(item) for item in attributes.items()))});")
            self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def log(self, *items):
        self.cursor.execute(f"INSERT INTO results {self.attributes[:len(items)]} VALUES {repr(items)};")
        self.db.commit()

    def close(self):
        self.db.close()
