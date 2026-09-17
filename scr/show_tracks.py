import sqlite3


connection = sqlite3.connect('music.db')
cursor = connection.cursor()

cursor.execute("SELECT * FROM tracks")
tracks = cursor.fetchall()

number = 1

for mus in tracks:
    print(str(number)+'.'+mus[1])
    number += 1

connection.close()

