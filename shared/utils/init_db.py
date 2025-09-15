import os
import logging
from sqlalchemy import Table, Column, String, MetaData, select
from shared.utils.database import engine
from dotenv import load_dotenv

# Load environment variables to get user details for seeding
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

metadata = MetaData()

# Define the 'users' table structure
users_table = Table('users', metadata,
    Column('user_id', String(255), primary_key=True),
    Column('dhan_client_id', String(255), nullable=False),
    Column('dhan_access_token', String(1024), nullable=False)
)

def initialize_database():
    """
    Creates tables and seeds the initial user if necessary.
    """
    try:
        logger.info("Initializing database and creating tables if they don't exist...")
        metadata.create_all(engine)
        logger.info("Database tables checked/created successfully.")

        # --- Seed the initial user data ---
        USER_ID = os.getenv("USER_ID")
        DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
        DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

        if not all([USER_ID, DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN]):
            logger.warning("Skipping user seeding because USER_ID, DHAN_CLIENT_ID, or DHAN_ACCESS_TOKEN is not set in .env file.")
            return

        with engine.connect() as conn:
            # Check if the user already exists
            user_exists = conn.execute(
                select(users_table).where(users_table.c.user_id == USER_ID)
            ).first()

            if not user_exists:
                logger.info(f"Seeding database with initial data for user: {USER_ID}")
                conn.execute(
                    users_table.insert().values(
                        user_id=USER_ID,
                        dhan_client_id=DHAN_CLIENT_ID,
                        dhan_access_token=DHAN_ACCESS_TOKEN
                    )
                )
                conn.commit() # Commit the transaction
                logger.info("User data seeded successfully.")
            else:
                logger.info(f"User {USER_ID} already exists. Skipping seeding.")

    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise

if __name__ == "__main__":
    initialize_database()