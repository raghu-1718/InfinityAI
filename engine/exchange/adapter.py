import abc, asyncio, time, uuid
from typing import Any, Dict, AsyncGenerator

class ExchangeAdapter(abc.ABC):
    @abc.abstractmethod
    async def get_depth(self, symbol: str) -> Dict[str, Any]: ...
    @abc.abstractmethod
    async def place_order(self, symbol: str, side: str, qty: float, order_type='market') -> Dict[str, Any]: ...
    @abc.abstractmethod
    async def cancel_order(self, order_id: str) -> bool: ...
    @abc.abstractmethod
    async def stream_orders(self) -> AsyncGenerator[Dict[str, Any], None]: ...

class MockAdapter(ExchangeAdapter):
    def __init__(self):
        self._orders: dict[str, Dict[str, Any]] = {}
    async def get_depth(self, symbol: str):
        return {'symbol': symbol, 'bid': 100.0, 'ask': 100.1, 'ts': time.time()}
    async def place_order(self, symbol: str, side: str, qty: float, order_type='market'):
        oid = str(uuid.uuid4())
        rec = {'order_id': oid, 'symbol': symbol, 'side': side, 'qty': qty, 'status': 'ACCEPTED'}
        self._orders[oid] = rec
        asyncio.create_task(self._fill(oid))
        return rec
    async def _fill(self, oid: str):
        await asyncio.sleep(0.3)
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
