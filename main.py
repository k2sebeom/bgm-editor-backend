from src.db import client

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await client.connect()

@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()

@app.get("/")
def read_root():
    return {"version": "0.1.0"}

@app.get("/api/metric/")
async def get_metric():
    genres = [g['genre'] for g in (await client.song.group_by(by=['genre']))]
    moods = [g['mood'] for g in (await client.song.group_by(by=['mood']))]
    return { "data": {
        "genre": genres,
        "mood": moods
    } }

@app.get("/api/song/")
async def get_songs(mood: str, genre: str, limit: int = 1):
    songs = await client.song.find_many(take=limit, where={
        "genre": genre,
        "mood": mood
    })
    return { "data": songs }
