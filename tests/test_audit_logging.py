import pytest
from fastapi import Request
from core.audit_logging import log_request
import logging

class DummyRequest:
    def __init__(self, method, url):
        self.method = method
        self.url = url

@pytest.mark.asyncio
def test_log_request(caplog):
    req = DummyRequest("GET", "https://www.infinityai.pro/test")
    with caplog.at_level(logging.INFO):
        import asyncio
        asyncio.run(log_request(req))
    assert any("Request: GET https://www.infinityai.pro/test" in m for m in caplog.messages)
