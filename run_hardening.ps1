param(
  [string]$Branch = "hardening/phase0"
)

$ErrorActionPreference = "Stop"

function Exec($c){Write-Host ">> $c" -ForegroundColor Cyan; & powershell -NoLogo -NoProfile -Command $c}

if (-not (Test-Path .git)) { Write-Error "Not in repo root"; exit 1 }

Exec "git fetch origin"

# Stash local changes if any
if (git status --porcelain) {
  Exec "git add -u"
  Exec "git stash push -m auto-hardening-prep"
}

# Sync main
Exec "git checkout main"
Exec "git reset --hard origin/main"

# Create / update branch
if (git rev-parse --verify $Branch 2>$null) {
  Exec "git switch $Branch"
  Exec "git rebase origin/main"
} else {
  Exec "git switch -c $Branch origin/main"
}

# Reapply stash
if (git stash list | Select-String auto-hardening-prep) { Exec "git stash pop" }

# Ensure dirs
New-Item -ItemType Directory -Force -Path config,risk,core,engine/exchange/brokers | Out-Null

Set-Content core/config.py @"
import os
from functools import lru_cache

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    TESTING = os.getenv("TESTING", "0") == "1"
    DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", "4000"))
    BROKER = os.getenv("BROKER", "MOCK").upper()
    DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")
    DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "")
    ANGEL_API_KEY = os.getenv("ANGEL_API_KEY", "")
    ANGEL_API_SECRET = os.getenv("ANGEL_API_SECRET", "")
    FIVEPAISA_APP_NAME = os.getenv("FIVEPAISA_APP_NAME", "")
    FIVEPAISA_CLIENT_CODE = os.getenv("FIVEPAISA_CLIENT_CODE", "")
    FIVEPAISA_PASSWORD = os.getenv("FIVEPAISA_PASSWORD", "")
    FIVEPAISA_ENCRYPTION_KEY = os.getenv("FIVEPAISA_ENCRYPTION_KEY", "")
    CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")
    OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    SHADOW_MODE = os.getenv("SHADOW_MODE", "0") == "1"

@lru_cache
def get_settings():
    return Settings()
"@

Set-Content risk/kill_switch.py @"
from datetime import date
from threading import Lock

class KillSwitch:
    def __init__(self, daily_loss_limit: float = 0):
        self._active = False
        self._lock = Lock()
        self.daily_loss_limit = daily_loss_limit
        self._loss_today = 0.0
        self._loss_date = date.today()

    def activate(self, reason: str = ""):
        with self._lock:
            self._active = True

    def deactivate(self):
        with self._lock:
            self._active = False

    def reset_if_new_day(self):
        with self._lock:
            if self._loss_date != date.today():
                self._loss_date = date.today()
                self._loss_today = 0.0

    def record_pnl(self, realized_delta: float):
        self.reset_if_new_day()
        if realized_delta < 0:
            with self._lock:
                self._loss_today += -realized_delta
                if self.daily_loss_limit > 0 and self._loss_today >= self.daily_loss_limit:
                    self._active = True

    def is_active(self):
        self.reset_if_new_day()
        return self._active

    def status(self):
        return {
            "active": self._active,
            "loss_today": self._loss_today,
            "daily_loss_limit": self.daily_loss_limit,
            "date": str(self._loss_date),
        }

_kill = None

def init_kill_switch(limit: float):
    global _kill
    if _kill is None:
        _kill = KillSwitch(limit)
    return _kill

def get_kill_switch():
    return _kill
"@

Set-Content engine/exchange/adapter.py @"
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
"@

Set-Content engine/exchange/__init__.py @"
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
"@

Set-Content engine/exchange/brokers/dhan.py @"
import asyncio, time, uuid
from typing import Any, Dict, AsyncGenerator
from ..adapter import ExchangeAdapter

class DhanAdapter(ExchangeAdapter):
    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token
        self._orders: dict[str, Dict[str, Any]] = {}
    async def get_depth(self, symbol: str):
        return {'symbol': symbol, 'bid': 100.0, 'ask': 100.2, 'ts': time.time()}
    async def place_order(self, symbol: str, side: str, qty: float, order_type='market'):
        oid = str(uuid.uuid4())
        rec = {'order_id': oid, 'symbol': symbol, 'side': side, 'qty': qty, 'status': 'ACCEPTED'}
        self._orders[oid] = rec
        asyncio.create_task(self._fill(oid))
        return rec
    async def _fill(self, oid: str):
        await asyncio.sleep(0.4)
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
            await asyncio.sleep(0.6)
"@

Set-Content engine/exchange/brokers/angel.py @"
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
"@

Set-Content engine/exchange/brokers/fivepaisa.py @"
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
"@

Set-Content config/.env.example @"
DATABASE_URL=mysql+pymysql://user:password@host:3306/infinityai
TESTING=0
SECRET_KEY=replace-me
ACCESS_TOKEN_EXPIRE_MINUTES=30
DAILY_LOSS_LIMIT=4000
BROKER=MOCK
DHAN_CLIENT_ID=replace-client-id
DHAN_ACCESS_TOKEN=replace-access-token
ANGEL_API_KEY=replace-angel-key
ANGEL_API_SECRET=replace-angel-secret
FIVEPAISA_APP_NAME=replace-app
FIVEPAISA_CLIENT_CODE=replace-client
FIVEPAISA_PASSWORD=replace-pass
FIVEPAISA_ENCRYPTION_KEY=replace-key
CORS_ALLOW_ORIGINS=http://localhost:3000
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
SHADOW_MODE=0
"@

git add core/config.py risk/kill_switch.py engine/exchange config/.env.example .flake8

if (git diff --cached --name-only) {
  Exec "git commit -m 'feat: phase0 hardening (config, adapters, kill switch)'"
  Exec "git push -u origin $Branch"
} else {
  Write-Host "No changes to commit."
}

Write-Host "Done. Open PR for $Branch"