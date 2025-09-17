# .github/scripts/init_db.py
import sys
import logging
from shared.utils.init_db import initialize_database

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        initialize_database()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        sys.exit(1)
