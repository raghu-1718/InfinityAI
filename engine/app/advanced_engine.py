import asyncio
from shared.utils.logger import get_logger
from core.broker.dhan_adapter import DhanAdapter
from core.strategies.advanced_breakout import AdvancedBreakoutStrategy

logger = get_logger("AdvancedEngine")

class AdvancedEngine:
    """
    The main engine that orchestrates the trading strategy,
    data feed, and execution.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.is_running = False
        self.broker = None
        self.strategy = None
        logger.info(f"Initializing AdvancedEngine for user: {self.user_id}")
        try:
            self.broker = DhanAdapter(user_id=self.user_id)
            logger.info("Broker adapter initialized successfully.")

            self.strategy = AdvancedBreakoutStrategy(broker=self.broker)
            logger.info("Trading strategy loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize engine components: {e}", exc_info=True)
            raise

    async def start(self):
        """
        Starts the main trading loop of the engine.
        """
        if not self.broker or not self.strategy:
            logger.error("Cannot start engine, broker or strategy is not available.")
            return

        self.is_running = True
        logger.info("Advanced Trading Engine started.")

        while self.is_running:
            try:
                logger.info("Executing strategy cycle...")
                await self.strategy.run_once() 
                logger.info("Strategy cycle complete. Waiting for next cycle.")
            except Exception as e:
                logger.error(f"An error occurred during the strategy cycle: {e}", exc_info=True)
            
            await asyncio.sleep(60) 

    async def stop(self):
        """
        Stops the engine gracefully.
        """
        self.is_running = False
        logger.info("Stopping Advanced Trading Engine...")