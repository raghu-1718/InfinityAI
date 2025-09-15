import os
from dotenv import load_dotenv
from shared.utils.logger import get_logger
from shared.utils.database import get_db_connection
from sqlalchemy.sql import text

# It's better to load environment variables at the start of the module
load_dotenv() 
logger = get_logger(__name__)

def get_user_credentials(user_id: str):
    """
    Retrieves user credentials securely from the SingleStore database.
    Assumes a 'users' table with columns: user_id, dhan_client_id, dhan_access_token.
    
    Args:
        user_id (str): The identifier for the user.

    Returns:
        dict: A dictionary containing the client_id and access_token, or None if not found.
    """
    query = text("SELECT dhan_client_id, dhan_access_token FROM users WHERE user_id = :user_id")
    
    conn = None
    try:
        conn = get_db_connection()
        result = conn.execute(query, {"user_id": user_id}).fetchone()
        
        if result:
            client_id, access_token = result
            logger.info(f"Successfully retrieved credentials for user_id: {user_id} from DB")
            return {"client_id": client_id, "access_token": access_token}
        else:
            logger.warning(f"Credentials not found in database for user_id: {user_id}")
            return None

    except Exception as e:
        logger.error(f"DB error retrieving credentials for {user_id}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close() # Returns the connection to the pool
