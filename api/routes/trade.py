from fastapi import APIRouter, HTTPException, Depends, Request
from core.usermanager import get_user_credentials
from core.broker.dhan_adapter import DhanAdapter
from core.tradelogger import log_trade

router = APIRouter()

@router.post("/trade/place")
async def place_trade(request: Request):
    """
    Place a trade via Dhan for the authenticated user.
    Expects JSON: {"user_id": ..., "symbol": ..., "action": ..., "quantity": ..., "order_type": ..., "price": ..., "product_type": ..., "exchange_segment": ...}
    """
    data = await request.json()
    user_id = data.get("user_id")
    creds = get_user_credentials(user_id)
    if not creds or not creds.get("dhan_client_id") or not creds.get("dhan_access_token"):
        raise HTTPException(status_code=403, detail="Dhan credentials not found for user.")
    try:
        dhan = DhanAdapter(user_id)
        result = dhan.execute_trade(
            security_id=data["symbol"],
            transaction_type=data["action"],
            quantity=int(data["quantity"]),
            order_type=data["order_type"],
            price=float(data["price"]),
            product_type=data["product_type"],
            exchange_segment=data["exchange_segment"]
        )
        log_trade(user_id, data)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trade placement failed: {str(e)}")
