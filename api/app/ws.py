# Example WebSocket endpoint for FastAPI
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Market data: {data}")
