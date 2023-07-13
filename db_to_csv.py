import sqlite3
import os

import mysql.connector

import config

filename = 'results'
if not os.path.exists(config.RESULT_DIR):
    os.mkdir(config.RESULT_DIR)
# connection = sqlite3.connect(f'{config.RESULT_DIR}/{filename}.db')
connection = mysql.connector.connect(
    host=config.MYSQL_HOST,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD
)
cursor = connection.cursor()
cursor.execute("USE results;")
cursor.execute("SELECT * FROM results;")
result = cursor.fetchall()
with open(f"{config.RESULT_DIR}/{filename}.csv", "w", encoding="utf-8") as f:
    robot_max_cnt = 10
    # f.write("Action,JustStarted,FollowingWall,JustStartedDelta,FollowingWallDelta\n")
    f.write("no,site_width,site_height,room_cnt,injury_cnt,departure_position,robot_type,robot_cnt,mode,room_visited,"
            "injury_rescued,returned,total_action_cnt,"
            f"{','.join(('robot_{}_visits,robot_{}_rescues,robot_{}_collides'.format(i, i, i) for i in range(robot_max_cnt)))}\n")
    for row in result:
        for col in row:
            print(col, end=",", file=f)
        print(file=f)
