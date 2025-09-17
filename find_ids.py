import pandas as pd
from dhanhq import dhanhq
from core.usermanager import get_user_credentials
import os

# --- Configuration ---
USER_ID = 'raghu_test_1'
# We will search for these terms within the trading symbols
SEARCH_TERMS = ['NIFTY', 'SENSEX']
# --- End Configuration ---

def find_instrument_details():
    """
    Downloads the Dhan security list and finds details for specified instruments using a broader search.
    """
    print("Attempting to find instrument details with a broader search...")

    try:
        credentials = get_user_credentials(USER_ID)
    except Exception as e:
        print(f"Could not get credentials. Make sure you are running this script from the 'InfinityAI.Pro' root directory. Error: {e}")
        return

    if not credentials:
        print(f"Could not find credentials for user: {USER_ID}. Please ensure the user is in the database.")
        return

    dhan = dhanhq(credentials['client_id'], credentials['access_token'])

    print("Downloading security list from Dhan...")
    try:
        securities_df = pd.DataFrame(dhan.fetch_security_list())
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download securities list: {e}")
        return

    # Use the correct column name 'SEM_INSTRUMENT_NAME'
    indices_df = securities_df[securities_df['SEM_INSTRUMENT_NAME'] == 'INDEX'].copy()

    print("\n--- Found Instrument Details (Broad Search) ---\n")

    found_any = False
    for term in SEARCH_TERMS:
        # Use .str.contains() for a case-insensitive search
        result_df = indices_df[indices_df['SEM_TRADING_SYMBOL'].str.contains(term, case=False, na=False)]

        if not result_df.empty:
            found_any = True
            print(f"Results for term: '{term}'")
            print(result_df[['SEM_TRADING_SYMBOL', 'SEM_SMST_SECURITY_ID', 'SEM_EXM_EXCH_ID', 'SEM_SEGMENT']])
            print("-" * 70)

    if not found_any:
        print("\nCould not find any instruments containing the search terms.")

if __name__ == "__main__":
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.width', 1000)

    find_instrument_details()
