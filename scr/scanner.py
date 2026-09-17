from pathlib import Path
import sqlite3

def find_music_files():
    m_folder = Path('music')
    formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma']

    music_files = []

    for f in m_folder.iterdir():
        if f.is_file() and f.suffix.lower() in formats:
            music_files.append(f)
    
    return music_files

def track_import(file):
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tracks WHERE filename = ?",
        (str(file.name),)
    )

    exsiting_track = cursor.fetchone()

    if exsiting_track is None:
        cursor.execute(
            """
            INSERT INTO tracks (filename, extension, path) VALUES (?, ?, ?)
            """,
            (str(file.name), str(file.suffix.lower()), str(file))
        )
        connection.commit()
        print("Добавлен трек:", file.name)
    else:
        print("Уже существует в базе:", str(file.name))
    
    connection.close()

music_files = find_music_files()

for f in music_files:
    track_import(f)