from glob import glob
import sys
from os import path
import json

from prisma import Prisma


async def sync(data):
    print(data)
    await client.song.create_many(data)
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
        title = path.splitext(fpath)[0]
        song = index[title]
        song['url'] = f'/youtube/{title}.mp3'
        add(song)
    sync(data)
    input("")
