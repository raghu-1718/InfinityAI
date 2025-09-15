# Prometheus metrics example for FastAPI
from prometheus_client import Summary, make_asgi_app
from fastapi import FastAPI

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
app = FastAPI()

@app.get("/metrics")
async def metrics():
    asgi_app = make_asgi_app()
    return await asgi_app(None, None)

@REQUEST_TIME.time()
def process_request():
    import time, random
    time.sleep(random.random())

@app.get("/simulate")
async def simulate():
    process_request()
    return {"status": "simulated"}
