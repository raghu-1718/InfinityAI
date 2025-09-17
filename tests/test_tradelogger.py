import pytest
from core.tradelogger import log_trade, get_trade_logs

class DummySession:
    def __init__(self):
        self.trades = []
    def add(self, trade):
        self.trades.append(trade)
    def commit(self):
        pass
    def close(self):
        pass
    def query(self, model):
        session_trades = self.trades
        class Q:
            def filter_by(self, user_id):
                filtered = [t for t in session_trades if getattr(t, 'user_id', None) == user_id]
                class O:
                    def order_by(self, *args, **kwargs):
                        class L:
                            def limit(self, n):
                                class All:
                                    def all(self):
                                        return filtered[:n]
                                return All()
                        return L()
                return O()
        return Q()

class DummyTrade:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

import core.tradelogger

def test_log_trade(monkeypatch):
    dummy_session = DummySession()
    monkeypatch.setattr("core.tradelogger.SessionLocal", lambda: dummy_session)
    monkeypatch.setattr("core.tradelogger.TradeLog", DummyTrade)
    log_trade(1, {"symbol": "AAPL", "action": "buy", "quantity": 10, "price": 100.0})
    assert len(dummy_session.trades) == 1
    assert dummy_session.trades[0].symbol == "AAPL"
    assert dummy_session.trades[0].action == "buy"

def test_get_trade_logs(monkeypatch):
    dummy_session = DummySession()
    dummy_session.trades.append(DummyTrade(user_id=1, symbol="AAPL", action="buy", quantity=10, price=100.0, timestamp="now"))
    monkeypatch.setattr("core.tradelogger.SessionLocal", lambda: dummy_session)
    logs = get_trade_logs(1)
    assert isinstance(logs, list)
    assert logs[0]["symbol"] == "AAPL"
    assert logs[0]["action"] == "buy"
