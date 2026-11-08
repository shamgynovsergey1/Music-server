
import sqlite3


def get_connection():
    connection = sqlite3.connect("music.db")
    connection.row_factory = sqlite3.Row
    return connection


def get_all_tracks():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT filename, extension, path FROM tracks"
        )
        return [dict(track) for track in cursor.fetchall()]
    finally:
        connection.close()


def search_tracks(search_text):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT filename, extension, path
            FROM tracks
            WHERE filename LIKE ?
            ORDER BY filename COLLATE NOCASE
        """, (f"%{search_text}%",))

        return [dict(track) for track in cursor.fetchall()]

    finally:
        connection.close()


def get_track(filename):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT filename, extension, path
            FROM tracks
            WHERE filename = ?
            """,
            (filename,),
        )
        track = cursor.fetchone()

        return dict(track) if track is not None else None
    finally:
        connection.close()


def get_tracks_count():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM tracks")
        return cursor.fetchone()[0]
    finally:
        connection.close()


def get_track_path(filename):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT path FROM tracks WHERE filename = ?",
            (filename,),
        )
        track = cursor.fetchone()

        return track["path"] if track is not None else None
    finally:
        connection.close()


def get_tracks_by_extension():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT extension, COUNT(*) AS tracks_count
            FROM tracks
            GROUP BY extension
            ORDER BY extension
        """)

        return {
            row["extension"]: row["tracks_count"]
            for row in cursor.fetchall()
        }

    finally:
        connection.close()


from pathlib import Path

def get_music_size():
    music_folder = Path("music")
    total_bytes = 0

    if not music_folder.exists():
        return 0

    for file_path in music_folder.iterdir():
        if file_path.is_file():
            if file_path.suffix.lower() in {
                ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"
            }:
                total_bytes += file_path.stat().st_size

    return round(total_bytes / (1024 * 1024), 2)


def check_library_integrity():
    music_folder = Path("Music")
    formats = {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"
    }

    # Получаем файлы, которые физически лежат в папке
    disk_files = []

    if music_folder.exists():
        for file in music_folder.iterdir():
            if file.is_file() and file.suffix.lower() in formats:
                disk_files.append(file)

    # Получаем записи из базы
    database_tracks = get_all_tracks()

    disk_names = {
        file.name.lower()
        for file in disk_files
    }

    database_names = {
        track["filename"].lower()
        for track in database_tracks
    }

    # Файлы есть на диске, но нет в базе
    files_not_in_database = [
        file.name
        for file in disk_files
        if file.name.lower() not in database_names
    ]

    # Записи есть в базе, но файлы отсутствуют
    missing_files = [
        track["filename"]
        for track in database_tracks
        if not Path(track["path"]).is_file()
    ]

    return {
        "disk_files_count": len(disk_files),
        "database_tracks_count": len(database_tracks),
        "files_not_in_database": files_not_in_database,
        "missing_files": missing_files,
        "is_synchronized": (
            len(files_not_in_database) == 0
            and len(missing_files) == 0
        )
    }