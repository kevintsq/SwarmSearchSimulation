import sqlite3
connection = sqlite3.connect('results.db')
cursor = connection.cursor()
result = cursor.execute("SELECT * FROM results")
with open("results.csv", "w", encoding="utf-8") as f:
    for row in result:
        for col in row:
            print(col, end=",", file=f)
        print(file=f)
