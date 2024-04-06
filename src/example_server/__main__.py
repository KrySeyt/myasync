import asyncio

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def route() -> str:
    await asyncio.sleep(2)
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run(app)
