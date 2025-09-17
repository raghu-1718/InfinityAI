import sys
import os
from datetime import date, timedelta

# --- Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- End Path Correction ---

from dhanhq import dhanhq
from core.usermanager import get_user_credentials
from shared.utils.logger import get_logger

logger = get_logger("HistoryTest")

def test_index_history():
    """
    A focused test to fetch historical data for a single index.
    """
    USER_ID = 'raghu_test_1'

    # --- Parameters to Test ---
    SECURITY_ID = '13'
    EXCHANGE_SEGMENT = 'NSE_IDX'
    INSTRUMENT_TYPE = 'INDEX'
    # --------------------------

    logger.info(f"Attempting to fetch historical data for Index ID: {SECURITY_ID}")

    try:
        credentials = get_user_credentials(USER_ID)
        if not credentials:
            logger.error(f"Credentials not found for user {USER_ID}")
            return

        dhan = dhanhq(credentials['client_id'], credentials['access_token'])

        to_date = str(date.today() - timedelta(days=1))
        from_date = str(date.today() - timedelta(days=5))

        logger.info(f"Calling historical_daily_data with:")
        logger.info(f"  security_id='{SECURITY_ID}'")
        logger.info(f"  exchange_segment='{EXCHANGE_SEGMENT}'")
        logger.info(f"  instrument_type='{INSTRUMENT_TYPE}'")
        logger.info(f"  from_date='{from_date}'")
        logger.info(f"  to_date='{to_date}'")

        response = dhan.historical_daily_data(
            security_id=SECURITY_ID,
            exchange_segment=EXCHANGE_SEGMENT,
            instrument_type=INSTRUMENT_TYPE,
            from_date=from_date,
            to_date=to_date
        )

        logger.info("--- API Response ---")
        logger.info(response)
        logger.info("--- End of Response ---")

        if response.get('status') == 'success':
            logger.info("Successfully fetched data!")
        else:
            logger.error("Failed to fetch data.")

    except Exception as e:
        logger.error(f"An exception occurred: {e}", exc_info=True)

if __name__ == '__main__':
    test_index_history()
