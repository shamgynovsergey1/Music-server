from pathlib import Path

def find_music_files():
    m_folder = Path('music')
    formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma']

    music_files = []

    for f in m_folder.iterdir():
        if f.is_file() and f.suffix.lower() in formats:
            music_files.append(f)
    
    return music_files

music = find_music_files()
    
print("Найдено треков:", len(music))

number = 1
for f in music:
    print(str(number) + "." + f.name)
    number += 1
