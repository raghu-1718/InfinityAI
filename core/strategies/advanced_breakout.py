import asyncio
<<<<<<< HEAD
from datetime import date, timedelta
from shared.utils.logger import get_logger
from core.broker.dhan_adapter import DhanAdapter

logger = get_logger("AdvancedBreakoutStrategy")

class AdvancedBreakoutStrategy:
    """
    A strategy that looks for price breakouts above a certain level.
    """
    def __init__(self, broker: DhanAdapter):
        self.broker = broker
        self.security_id = '1333' # SBIN (State Bank of India)
        self.exchange = "NSE_EQ" 
        self.lookback_period = 20 # Look at the last 20 days for the breakout
        logger.info("Advanced Breakout Strategy initialized for SBIN (ID: 1333).")

    async def run_once(self):
        """
        Executes a single cycle of the strategy logic.
        """
        logger.info(f"Running breakout analysis for security ID: {self.security_id}")

        try:
            to_date = date.today()
            from_date = to_date - timedelta(days=self.lookback_period * 2)

            logger.info(f"Fetching historical data for the last {self.lookback_period} trading days...")
            
            hist_data = self.broker.dhan.historical_daily_data(
                security_id=self.security_id,
                exchange_segment=self.exchange,
                instrument_type='EQUITY',
                from_date=str(from_date),
                to_date=str(to_date)
            )

            if hist_data.get('status') == 'success' and hist_data.get('data', {}).get('high'):
                all_high_prices = hist_data['data']['high']
                recent_highs = all_high_prices[-self.lookback_period:]
                breakout_level = max(recent_highs)
                
                logger.info(f"Calculated {self.lookback_period}-day breakout level: {breakout_level}")

                # --- Get LTP and compare ---
                ltp = self.broker.get_ltp(security_id=self.security_id, exchange_segment=self.exchange)
                
                if ltp > 0 and ltp > breakout_level:
                    logger.info(f"!!! BREAKOUT DETECTED !!! LTP ({ltp}) > Breakout Level ({breakout_level}).")
                    # --- Future Step: Place buy order ---
                    # logger.info("Placing buy order...")
                    # self.broker.execute_trade(...)
                elif ltp > 0:
                    logger.info(f"No breakout. LTP ({ltp}) <= Breakout Level ({breakout_level}).")
                else:
                    logger.warning("Could not get valid LTP to check for breakout.")

            else:
                logger.warning(f"Could not fetch historical data or data was empty. API Response: {hist_data}")

        except Exception as e:
            logger.error(f"An error occurred during breakout analysis: {e}", exc_info=True)
=======
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
import logging

from core.market_data.feed_manager import MarketTick
from core.execution.order_manager import Order, OrderType

logger = logging.getLogger(__name__)

@dataclass
class BreakoutSignal:
    symbol: str
    direction: str  # "LONG" or "SHORT"
    entry_price: float
    stop_loss: float
    target: float
    confidence: float
    timestamp: datetime
    volume_confirmation: bool = False
    momentum_confirmation: bool = False

class AdvancedBreakoutStrategy:
    ... # full implementation from TradingAI-Pro
>>>>>>> 7ee6d5f999d9bc01dbdc4b984f791a0af547bcda
