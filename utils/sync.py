from glob import glob
import sys
from os import path
import json

from prisma import Prisma
import asyncio


async def sync(client, data):
    await client.connect()
    for song in data:
        await client.song.create(song)
    await client.disconnect()
    print("Sync complete! It is okay to close")


if __name__ == "__main__":
    src_dir, src_file = sys.argv[1:]

    client = Prisma()

    audio_files = glob(path.join(src_dir, '*.mp3'))

    with open(src_file, 'r') as f:
        d = json.loads(f.read())
    
    index = dict()
    for song in d:
        index[song['title']] = song
    
    data = []
    add = data.append
    for fpath in audio_files:
        title = path.splitext(path.basename(fpath))[0]
        song = index[title]
        song['url'] = f'/youtube/{title}.mp3'
        add(song)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sync(client, data))
    
