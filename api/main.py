"""InfinityAI FastAPI Application (canonical entrypoint)."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from risk.kill_switch import init_kill_switch, get_kill_switch
from engine.exchange import get_adapter

try:
    # Optional observability (ignore if modules not present)
    from prometheus_fastapi_instrumentator import Instrumentator  # type: ignore
except ImportError:  # pragma: no cover
    Instrumentator = None  # type: ignore

settings = get_settings()

if not settings.TESTING and settings.SECRET_KEY == "dev-insecure":
    raise RuntimeError("SECURITY: SECRET_KEY must be set (non-default) in non-testing environments.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="InfinityAI Backend", version="0.1.0")

# CORS
origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Risk + Exchange
init_kill_switch(settings.DAILY_LOSS_LIMIT)
adapter = get_adapter()


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/health")
async def health() -> dict[str, Any]:
    ks = get_kill_switch()
    # Lightweight depth probe (non-fatal)
    broker_ok = True
    try:
        depth = await adapter.get_depth("HEALTH_SYMBOL")  # mock fast
        _ = depth.get("bid")
    except Exception:  # pragma: no cover
        broker_ok = False
    status = "ok" if broker_ok else "degraded"
    return {
        "status": status,
        "broker": settings.BROKER,
        "broker_ok": broker_ok,
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


# Optional metrics
if Instrumentator:
    Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")
