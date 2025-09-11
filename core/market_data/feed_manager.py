import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class FeedStatus(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"

@dataclass
class MarketTick:
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: float = 0.0
    ask: float = 0.0
    bid_size: int = 0
    ask_size: int = 0
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    close: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0

class MarketDataFeed:
    ... # full implementation from TradingAI-Pro

class FeedManager:
    ... # full implementation from TradingAI-Pro

feed_manager = FeedManager()
