from fastapi import FastAPI
import sqlite3

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Music server работает!"}


@app.get("/tracks")
def get_tracks():
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT filename FROM tracks"
    )

    tracks = cursor.fetchall()

    connection.close()

    return tracks