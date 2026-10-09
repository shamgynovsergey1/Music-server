from pathlib import Path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sqlite3


# Поиск музыкальных файлов в папке music
def find_music_files():
    m_folder = Path("music")
    formats = [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"]

    music_files = []

    for f in m_folder.iterdir():
        if f.is_file() and f.suffix.lower() in formats:
            music_files.append(f)

    return music_files


# Добавление трека в базу данных
def track_import(file):
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tracks WHERE filename = ?",
        (str(file.name),)
    )

    existing_track = cursor.fetchone()

    if existing_track is None:
        cursor.execute(
            """
            INSERT INTO tracks (filename, extension, path)
            VALUES (?, ?, ?)
            """,
            (
                str(file.name),
                str(file.suffix.lower()),
                str(file)
            )
        )

        connection.commit()
        print("Добавлен трек:", file.name)

    else:
        print("Уже существует в базе:", file.name)

    connection.close()


# Проверяем, закончилось ли копирование файла
def wait_until_ready(file):
    previous_size = -1
    stable_checks = 0

    for attempt in range(60):

        if not file.exists():
            return False

        current_size = file.stat().st_size

        if current_size == previous_size:
            stable_checks += 1
        else:
            stable_checks = 0

        if stable_checks >= 3:
            return True

        previous_size = current_size

        time.sleep(1)

    return False


# Обработчик событий Watchdog
class MusicHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        file = Path(event.src_path)

        formats = [
            ".mp3",
            ".wav",
            ".flac",
            ".aac",
            ".ogg",
            ".wma"
        ]

        if file.suffix.lower() not in formats:
            return

        print("Обнаружен новый трек:", file.name)
        print("Проверяю, завершилось ли копирование...")

        if wait_until_ready(file):

            print("Файл готов!")

            track_import(file)

        else:

            print("Файл не готов или исчез:", file.name)


# Создаём папку music, если её нет
music_folder = Path("music")
music_folder.mkdir(exist_ok=True)


# Проверяем уже существующие треки
print("Проверяю существующие треки...")

music_files = find_music_files()

for file in music_files:
    track_import(file)

print("Существующие треки проверены.")


# Запускаем Watchdog
observer = Observer()
handler = MusicHandler()

observer.schedule(
    handler,
    str(music_folder),
    recursive=False
)

observer.start()

print("Слежу за папкой music...")


# Бесконечно ждём новые файлы
try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("Остановка программы...")

    observer.stop()


observer.join()

print("Программа остановлена.")