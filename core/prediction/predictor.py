from typing import Dict, Optional
from datetime import date, timedelta
from core.broker.dhan_adapter import DhanAdapter
from shared.utils.logger import get_logger

logger = get_logger(__name__)

class DailyPredictor:
    """
    Calculates daily price predictions using technical indicators.
    """
    def __init__(self, dhan_adapter: DhanAdapter):
        self.dhan_adapter = dhan_adapter

    def _get_previous_day_ohlc(self, security_id: str, exchange_segment: str, instrument_type: str) -> Optional[Dict[str, float]]:
        """Fetches the previous trading day's OHLC data."""
        try:
            to_date = str(date.today() - timedelta(days=1))
            from_date = str(date.today() - timedelta(days=5))

            # Corrected: The function parameter is always 'security_id'.
            response = self.dhan_adapter.dhan.historical_daily_data(
                security_id=security_id,
                exchange_segment=exchange_segment,
                instrument_type=instrument_type,
                from_date=from_date,
                to_date=to_date
            )

            if response.get('status') == 'success' and response.get('data'):
                last_day = response['data'][-1]
                ohlc = {
                    'open': last_day['open'],
                    'high': last_day['high'],
                    'low': last_day['low'],
                    'close': last_day['close']
                }
                logger.info(f"Previous day OHLC for security ID {security_id}: {ohlc}")
                return ohlc
            else:
                logger.warning(f"Could not fetch historical data for security ID {security_id}. Response: {response}")
                return None
        except Exception as e:
            logger.error(f"Error fetching previous day OHLC for security ID {security_id}: {e}", exc_info=True)
            return None

    def get_pivot_point_prediction(self, security_id: str, exchange_segment: str, instrument_type: str) -> Optional[Dict[str, float]]:
        """
        Calculates Pivot Points (PP) and first level Support/Resistance.
        """
        ohlc = self._get_previous_day_ohlc(security_id, exchange_segment, instrument_type)
        if not ohlc:
            return None

        high = ohlc['high']
        low = ohlc['low']
        close = ohlc['close']

        pivot_point = (high + low + close) / 3
        support1 = (2 * pivot_point) - high
        resistance1 = (2 * pivot_point) - low

        prediction = {
            'predicted_low': round(support1, 2),
            'predicted_high': round(resistance1, 2),
            'pivot_point': round(pivot_point, 2)
        }

        return prediction
