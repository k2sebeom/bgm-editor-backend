from src.db import client
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from uuid import uuid1
from os import path, remove


SRC_DIR = '../youtube-audio-library-crawler/dst'

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


@app.post("/api/process/")
async def process_video(background_tasks: BackgroundTasks, starts: List[str] = Form(), ends: List[str] = Form(), ids: List[str] = Form(), video: UploadFile = File()):
    temp_path = f'{uuid1()}-{video.filename}'
    background_tasks.add_task(remove, temp_path)
    with open(temp_path, 'wb') as f:
        f.write(await video.read())

    vclip = VideoFileClip(temp_path)

    aclips = []
    for clip_id in ids:
        clip = await client.song.find_unique(where={"id": int(clip_id)})
        aclips.append(AudioFileClip(path.join(SRC_DIR, path.basename(clip.url))))
    
    final_clips = [vclip.audio]
    for s, e, aclip in zip(starts, ends, aclips):
        r = [float(s), float(e)]
        r.sort()
        s, e = r
        final_clips.append(audio_fadeout(aclip.subclip(0, e - s).set_start(s), 1))
    final_aclip = CompositeAudioClip(final_clips)
    final_vclip = vclip.set_audio(final_aclip)
    temp_path = f'{uuid1()}-{video.filename}'
    background_tasks.add_task(remove, temp_path)
    final_vclip.write_videofile(temp_path, audio_codec='aac', audio_bitrate='192k')
    return FileResponse(path=temp_path)
