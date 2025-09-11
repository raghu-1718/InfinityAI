
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from core.usermanager import get_user_credentials
from core.tradelogger import log_trade
from core.telegramalerts import send_telegram

router = APIRouter()

@router.post("/api/dhan/callback")
async def dhan_callback(request: Request):
    data = await request.json()
    # Process Dhan access token and events here
    creds = get_user_credentials(data.get('user_id'))
    if not creds:
        return JSONResponse(content={"error": "User credentials not found"}, status_code=status.HTTP_403_FORBIDDEN)
    log_trade(data.get('user_id'), data)
    msg = f"Order Update {data.get('orderStatus')} {data.get('transactionType')} {data.get('tradingSymbol')} Qty: {data.get('quantity')}"
    send_telegram(creds.get('telegram_chat_id'), msg)
    return JSONResponse(content={"status": "success"}, status_code=status.HTTP_200_OK)
