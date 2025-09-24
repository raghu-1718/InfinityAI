"""FastAPI app composition and integrations (WSGI, CORS, RBAC)."""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from risk.kill_switch import init_kill_switch, get_kill_switch
from engine.exchange import get_adapter

settings = get_settings()
app = FastAPI(title="InfinityAI API")

origins = settings.CORS_ALLOW_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_kill_switch(settings.DAILY_LOSS_LIMIT)
adapter = get_adapter()


@app.get("/health")
def health() -> dict[str, Any]:
    ks = get_kill_switch()
    return {
        "status": "ok",
        "broker": settings.BROKER,
        "kill_switch": ks.status() if ks else None,
    }


@app.post("/admin/kill/activate")
def activate_kill() -> dict[str, str]:
    ks = get_kill_switch()
    ks.activate("manual")
    return {"message": "activated"}


@app.post("/admin/kill/deactivate")
def deactivate_kill() -> dict[str, str]:
    ks = get_kill_switch()
    ks.deactivate()
    return {"message": "deactivated"}


@app.get("/admin/kill/status")
def kill_status() -> dict[str, Any]:
    ks = get_kill_switch()
    return ks.status()


@app.post("/api/trade/order")
async def submit_order(symbol: str, side: str, qty: float):
    ks = get_kill_switch()
    if ks and ks.is_active():
        raise HTTPException(status_code=423, detail="Kill switch active")
    if side not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="Invalid side")
    return await adapter.place_order(symbol, side, qty)
