import asyncio, time, uuid
from typing import Any, Dict, AsyncGenerator
from ..adapter import ExchangeAdapter

class FivePaisaAdapter(ExchangeAdapter):
    def __init__(self, app_name: str, client_code: str, password: str, encryption_key: str):
        self.app_name = app_name
        self.client_code = client_code
        self.password = password
        self.encryption_key = encryption_key
        self._orders: dict[str, Dict[str, Any]] = {}
    async def get_depth(self, symbol: str):
        return {'symbol': symbol, 'bid': 100.1, 'ask': 100.3, 'ts': time.time()}
    async def place_order(self, symbol: str, side: str, qty: float, order_type='market'):
        oid = str(uuid.uuid4())
        rec = {'order_id': oid, 'symbol': symbol, 'side': side, 'qty': qty, 'status': 'ACCEPTED'}
        self._orders[oid] = rec
        asyncio.create_task(self._fill(oid))
        return rec
    async def _fill(self, oid: str):
        await asyncio.sleep(0.45)
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
            await asyncio.sleep(0.55)
