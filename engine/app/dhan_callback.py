from fastapi import APIRouter, Request, HTTPException
import json

# Create the APIRouter instance. This is the 'router' that main.py is looking for.
router = APIRouter(
    prefix="/callback",
    tags=["Broker Callbacks"]
)

@router.post("/dhan")
async def dhan_webhook_handler(request: Request):
    """
    Handles incoming webhook alerts from Dhan.
    This endpoint listens for POST requests and processes the payload.
    """
    try:
        payload = await request.json()

        # Here you would add your logic to process the trade alert from Dhan.
        # For now, we will just print it to the console.
        print(f"Received Dhan webhook payload: {payload}")

        return {"status": "success", "message": "Webhook received"}

    except json.JSONDecodeError:
        # This error happens if the request body is not valid JSON
        print("Error: Received invalid JSON in webhook payload.")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        # Catch other potential errors
        print(f"An error occurred processing the Dhan webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
