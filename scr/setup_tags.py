
import sqlite3

connection = sqlite3.connect("music.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS track_tags (
        track_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,

        PRIMARY KEY (track_id, tag_id),

        FOREIGN KEY (track_id) REFERENCES tracks(id)
            ON DELETE CASCADE,

        FOREIGN KEY (tag_id) REFERENCES tags(id)
            ON DELETE CASCADE
    )
""")

connection.commit()
connection.close()

print("Таблицы тегов успешно созданы!")
