import asyncio, time, uuid
from typing import Any, Dict, AsyncGenerator
from ..adapter import ExchangeAdapter

class AngelAdapter(ExchangeAdapter):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self._orders: dict[str, Dict[str, Any]] = {}
    async def get_depth(self, symbol: str):
        return {'symbol': symbol, 'bid': 99.9, 'ask': 100.0, 'ts': time.time()}
    async def place_order(self, symbol: str, side: str, qty: float, order_type='market'):
        oid = str(uuid.uuid4())
        self._orders[oid] = {'order_id': oid, 'symbol': symbol, 'side': side, 'qty': qty, 'status': 'ACCEPTED'}
        asyncio.create_task(self._fill(oid))
        return self._orders[oid]
    async def _fill(self, oid: str):
        await asyncio.sleep(0.35)
        if oid in self._orders:
            self._orders[oid]['status'] = 'FILLED'
    async def cancel_order(self, order_id: str):
        if order_id in self._orders:
            self._orders[order_id]['status'] = 'CANCELLED'
            return True
        return False
    async def stream_orders(self):
        while True:
            for o in list(self._orders.values()):
                yield o
            await asyncio.sleep(0.5)
