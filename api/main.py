from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include your routes here
# from app.routes import router
# app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
"""
This file has been moved to app/main.py for Docker compatibility with the Dockerfile.
"""
