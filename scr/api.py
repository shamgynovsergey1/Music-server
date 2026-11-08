
from pathlib import Path
from mimetypes import guess_type
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scr.database import (
    get_all_tracks,
    get_track,
    get_tracks_count,
    get_track_path,
    search_tracks,
    get_tracks_by_extension,
    get_music_size,
    check_library_integrity
)


# Создаём приложение FastAPI
app = FastAPI(
    title="Music Server",
    description="Мой личный сервер музыкальных демо",
    version="1.0.0",
)


# Формат данных одного трека для API
class Track(BaseModel):
    filename: str
    extension: str
    audio_url: str


# Главная страница API
@app.get("/")
def home():
    return {
        "message": "Музыкальный сервер работает!",
        "docs": "/docs",
        "player": "/app/",
    }


# Получение списка всех треков
@app.get("/tracks", response_model=list[Track])
def list_tracks():
    tracks = get_all_tracks()

    result = []

    for track in tracks:
        result.append(
            {
                "filename": track["filename"],
                "extension": track["extension"],
                "audio_url": (
                    "/tracks/"
                    + quote(track["filename"], safe="")
                    + "/file"
                ),
            }
        )

    return result

@app.get("/tracks/search", response_model=list[Track])
def find_tracks(q: str):
    tracks = search_tracks(q)

    result = []

    for track in tracks:
        result.append({
            "filename": track["filename"],
            "extension": track["extension"],
            "audio_url": (
                "/tracks/"
                + quote(track["filename"], safe="")
                + "/file"
            ),
        })

    return result


# Получение информации об одном треке
@app.get("/tracks/{filename}")
def track_info(filename: str):
    track = get_track(filename)

    if track is None:
        raise HTTPException(
            status_code=404,
            detail="Трек не найден в базе данных",
        )

    return {
        "filename": track["filename"],
        "extension": track["extension"],
        "path": track["path"],
    }



# Статистика библиотеки
@app.get("/stats")
def stats():
    formats = get_tracks_by_extension()

    return {
        "tracks_count": get_tracks_count(),
        "formats": formats,
        "formats_count": len(formats),
        "music_size_mb": get_music_size(),
    }

@app.get("/check-library")
def check_library():
    return check_library_integrity()


# Передача аудиофайла для воспроизведения
@app.get("/tracks/{filename}/file")
def play_track(filename: str):
    file_path = get_track_path(filename)

    if file_path is None:
        raise HTTPException(
            status_code=404,
            detail="Трек не найден в базе данных",
        )

    file = Path(file_path)

    if not file.is_file():
        raise HTTPException(
            status_code=404,
            detail="Аудиофайл не найден на диске",
        )

    media_type = guess_type(file.name)[0] or "application/octet-stream"

    return FileResponse(
        path=str(file),
        media_type=media_type,
        filename=file.name,
    )


# Подключаем веб-плеер
app.mount(
    "/app",
    StaticFiles(directory="frontend", html=True),
    name="frontend",
)
