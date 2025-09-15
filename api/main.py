from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
"""
This file has been moved to app/main.py for Docker compatibility with the Dockerfile.
"""
