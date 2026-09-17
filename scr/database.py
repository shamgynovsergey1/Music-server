import sqlite3

def create_database():
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        extension TEXT NOT NULL,
        path TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()

create_database()

print("йоу база есть")