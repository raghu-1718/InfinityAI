<<<<<<< HEAD
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dhanhq import dhanhq
from core.usermanager import get_user_credentials
from shared.utils.logger import get_logger
from datetime import date

logger = get_logger(__name__)

class DhanAdapter:
    """
    Adapter for interacting with the Dhan API.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        logger.info(f"Initializing DhanAdapter for user: {user_id}")
        
        credentials = get_user_credentials(user_id)
        if not credentials:
            logger.error(f"Failed to initialize DhanAdapter: Credentials not found for user {user_id}")
            raise ValueError(f"Credentials not found for user {user_id}")
        
        self.client_id = credentials['client_id']
        self.access_token = credentials['access_token']
        
        self.dhan = dhanhq(self.client_id, self.access_token)
        logger.info(f"DhanAdapter initialized successfully for user: {user_id}")

    def get_fund_limits(self) -> Dict[str, Any]:
        """Fetches fund limits."""
        logger.info(f"Fetching fund limits for client: {self.client_id}")
        return self.dhan.get_fund_limits()

    def get_order_list(self) -> Dict[str, Any]:
        """Fetches the list of orders."""
        logger.info(f"Fetching order list for client: {self.client_id}")
        return self.dhan.get_order_list()

    def get_ltp(self, security_id: str, exchange_segment: str) -> float:
        """Fetches the Last Traded Price for a security."""
        logger.info(f"Fetching LTP for security: {security_id}")
        try:
            today_str = str(date.today())
            # The correct method name is `intraday_minute_data`
            response = self.dhan.intraday_minute_data(
                security_id=security_id,
                exchange_segment=exchange_segment,
                instrument_type='EQUITY',
                from_date=today_str,
                to_date=today_str
            )
            
            if response.get('status') == 'success' and response.get('data', {}).get('close'):
                # The 'close' of the last candle is the most recent LTP
                ltp = response['data']['close'][-1]
                logger.info(f"LTP for {security_id} is {ltp}")
                return ltp
            else:
                logger.warning(f"Could not fetch LTP. API Response: {response}")
                return 0.0
        except Exception as e:
            logger.error(f"Error fetching LTP: {e}", exc_info=True)
            return 0.0

    def execute_trade(self, security_id: str, transaction_type: str, quantity: int, order_type: str, price: float, product_type: str, exchange_segment: str) -> Dict[str, Any]:
        """
        Places an order with the broker.
        """
        logger.info(f"Executing trade for {self.client_id}: {transaction_type} {quantity} of {security_id} @ {price}")
        
        from dhanhq import (
            SELL, BUY, MARKET, LIMIT,
            NSE_EQ, NSE_FNO, BSE_EQ, MCX_COMM,
            CNC, INTRADAY, MARGIN, MTF, CO, BO,
            DAY
        )

        transaction_map = {'BUY': BUY, 'SELL': SELL}
        order_type_map = {'MARKET': MARKET, 'LIMIT': LIMIT}
        exchange_map = {'NSE_FNO': NSE_FNO, 'NSE_EQ': NSE_EQ, 'BSE_EQ': BSE_EQ, 'MCX_COMM': MCX_COMM}
        product_type_map = {'CNC': CNC, 'INTRADAY': INTRADAY, 'MARGIN': MARGIN, 'MTF': MTF, 'CO': CO, 'BO': BO}

        try:
            return self.dhan.place_order(
                security_id=security_id,
                exchange_segment=exchange_map[exchange_segment],
                transaction_type=transaction_map[transaction_type],
                quantity=quantity,
                order_type=order_type_map[order_type],
                product_type=product_type_map[product_type],
                price=price,
                validity=DAY
            )
        except KeyError as e:
            logger.error(f"Invalid parameter for trade execution: {e}")
            raise ValueError(f"Invalid trade parameter provided: {e}")
        except Exception as e:
            logger.error(f"Order placement failed: {e}", exc_info=True)
            raise e

    async def get_quote_async(self, symbol: str) -> Optional[Any]:
        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(None, self.dhan.quote, {"exchange": "NSE", "symbol": symbol})
            return resp
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

    async def subscribe_market_feed(self, symbols: List[str], callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribes to the market feed using WebSockets."""
        import websockets
        import json
        ws_url = "wss://api.dhan.co/marketfeed"
        headers = {
            "access-token": self.access_token,
            "X-Client-Id": self.client_id,
        }
        subscribe_msg = {
            "action": "subscribe",
            "symbols": symbols,
            "feedType": "marketdata"
        }
        async with websockets.connect(ws_url, extra_headers=headers) as ws:
            await ws.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to market feed for {symbols}")
            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    callback(data)
                except Exception as e:
                    logger.error(f"Market feed error: {e}")
                    break
=======

import asyncio
from dhanhq import dhanhq, DhanContext  # type: ignore
import logging
from core.broker.retry import call_broker_api

logger = logging.getLogger(__name__)

from typing import Any, Callable, Dict, List, Optional

class DhanAdapter:
	context: 'DhanContext'  # type: ignore

	def __init__(self, client_id: str, access_token: str) -> None:
		self.context = DhanContext(client_id, access_token)  # type: ignore
		self.dhan = dhanhq(self.context)  # type: ignore

	def get_auth_headers(self) -> Dict[str, str]:
		return {
			"access-token": self.context.access_token,
			"X-Client-Id": self.context.client_id,
		}

	def get_profile(self) -> Optional[Any]:
		try:
			resp = self.dhan.profile()
			return resp
		except Exception as e:
			logger.error(f"Error fetching profile: {e}")
			return None

		# Example usage:
		# response = call_broker_api(broker_url, payload)
	def execute_trade(self, strategy: Dict[str, Any], creds: Dict[str, str]) -> Dict[str, Any]:
		if strategy["action"] == "HOLD":
			return {"status": "skipped", "reason": "HOLD action"}

		payload = {
			"transaction_type": strategy["action"],
			"exchange": "NSE",
			"symbol": strategy["symbol"],
			"quantity": strategy.get("quantity", 1),
			"product_type": "INTRADAY",
			"price": 0.0,
			"validity": "DAY",
			"order_type": "MARKET",
			"source": "API"
		}
		try:
			resp = self.dhan.place_order(payload)
			logger.info(f"Order placed: {resp}")
			return {
				"status": "success",
				"order_details": resp,
			}
		except Exception as e:
			logger.error(f"Order placement failed: {e}")
			return {
				"status": "error",
				"message": str(e),
			}

	async def get_quote_async(self, symbol: str) -> Optional[Any]:
		loop = asyncio.get_event_loop()
		try:
			resp = await loop.run_in_executor(None, self.dhan.quote, {"exchange": "NSE", "symbol": symbol})
			return resp
		except Exception as e:
			logger.error(f"Error fetching quote for {symbol}: {e}")
			return None

	async def subscribe_market_feed(self, symbols: List[str], callback: Callable[[Dict[str, Any]], None]) -> None:
		import websockets
		import json
		ws_url = "wss://api.dhan.co/marketfeed"
		headers = {
			"access-token": self.context.access_token,
			"X-Client-Id": self.context.client_id,
		}
		subscribe_msg = {
			"action": "subscribe",
			"symbols": symbols,
			"feedType": "marketdata"
		}
		async with websockets.connect(ws_url, extra_headers=headers) as ws:
			await ws.send(json.dumps(subscribe_msg))
			logger.info(f"Subscribed to market feed for {symbols}")
			while True:
				try:
					msg = await ws.recv()
					data = json.loads(msg)
					callback(data)
				except Exception as e:
					logger.error(f"Market feed error: {e}")
					break
>>>>>>> 7ee6d5f999d9bc01dbdc4b984f791a0af547bcda
