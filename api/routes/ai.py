
from fastapi import APIRouter, HTTPException, Request
from typing import List
from core.models import Model, Prediction, Signal, Backtest
from core.model_management import train_and_log_model, predict_with_model, list_registered_models, get_model_versions, monitor_drift
from shared.utils.database import db
import numpy as np

router = APIRouter()

@router.post("/train", tags=["AI/ML"])
async def train_model(request: Request):
    data = await request.json()
    X = np.array(data.get("X"))
    y = np.array(data.get("y"))
    model_name = data.get("model_name", "random_forest_model")
    params = data.get("params", {})
    result = train_and_log_model(X, y, model_name, params)
    return {"result": result}

@router.post("/predict", tags=["AI/ML"])
async def predict(request: Request):
    data = await request.json()
    model_uri = data.get("model_uri")
    X = np.array(data.get("X"))
    preds = predict_with_model(model_uri, X)
    return {"predictions": preds}

@router.get("/models", tags=["AI/ML"])
async def list_models():
    models = list_registered_models()
    return {"models": models}

@router.get("/models/{model_name}/versions", tags=["AI/ML"])
async def model_versions(model_name: str):
    versions = get_model_versions(model_name)
    return {"versions": [v.version for v in versions]}

@router.post("/drift", tags=["AI/ML"])
async def drift_monitor(request: Request):
    data = await request.json()
    reference = np.array(data.get("reference"))
    current = np.array(data.get("current"))
    report = monitor_drift(reference, current)
    return {"drift_report": report}

@router.get("/signals", tags=["AI/ML"])
async def get_signals():
    signals = db.session.query(Signal).all()
    return {"signals": [s.__dict__ for s in signals]}

@router.post("/backtest", tags=["AI/ML"])
async def run_backtest(request: Request):
    data = await request.json()
    # Placeholder: implement backtest logic
    return {"status": "Backtest started", "params": data}
