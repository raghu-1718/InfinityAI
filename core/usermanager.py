<<<<<<< HEAD
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
=======

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import User, Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///infinityai.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_user_credentials(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    if user:
        return {
            "username": user.username,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "role": user.role
        }
    return None
>>>>>>> 7ee6d5f999d9bc01dbdc4b984f791a0af547bcda
