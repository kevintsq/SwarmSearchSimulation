import sqlite3

filename = 'results_small_ljy'
connection = sqlite3.connect(f'{filename}.db')
cursor = connection.cursor()
result = cursor.execute("SELECT * FROM results WHERE robot_cnt < 11 AND mode = 'Search' AND (total_action_cnt = 1000 OR room_cnt = room_visited)")
with open(f"{filename}_filtered.csv", "w", encoding="utf-8") as f:
    robot_max_cnt = 10
    f.write("no,site_width,site_height,room_cnt,injury_cnt,departure_position,robot_type,robot_cnt,mode,room_visited,"
            "injury_rescued,returned,total_action_cnt,"
            f"{','.join(('robot_{}_visits,robot_{}_rescues,robot_{}_collides'.format(i, i, i) for i in range(robot_max_cnt)))}\n")
    for row in result:
        for col in row:
            print(col, end=",", file=f)
        print(file=f)
