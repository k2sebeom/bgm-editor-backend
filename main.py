from src.db import client

from fastapi import FastAPI


app = FastAPI()

@app.on_event("startup")
async def startup():
    await client.connect()

@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()

@app.get("/")
def read_root():
    return {"version": "1.0.0"}