from core.config import get_settings
from .adapter import ExchangeAdapter, MockAdapter
from .brokers.dhan import DhanAdapter
from .brokers.angel import AngelAdapter
from .brokers.fivepaisa import FivePaisaAdapter

def get_adapter() -> ExchangeAdapter:
    s = get_settings()
    if s.BROKER == 'DHAN':
        return DhanAdapter(s.DHAN_CLIENT_ID, s.DHAN_ACCESS_TOKEN)
    if s.BROKER == 'ANGEL':
        return AngelAdapter(s.ANGEL_API_KEY, s.ANGEL_API_SECRET)
    if s.BROKER == 'FIVEPAISA':
        return FivePaisaAdapter(
            s.FIVEPAISA_APP_NAME,
            s.FIVEPAISA_CLIENT_CODE,
            s.FIVEPAISA_PASSWORD,
            s.FIVEPAISA_ENCRYPTION_KEY
        )
    return MockAdapter()
