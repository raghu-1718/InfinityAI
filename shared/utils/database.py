import os
import time
import logging
import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager

# Setup logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database manager for MySQL with connection pooling, retry logic,
    and proper error handling for Azure MySQL Flexible Server.
    """
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self, pool_size: int = 5):
        """Initialize the connection pool with retry logic."""
        max_retries = 5
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Get connection parameters from environment variables
                db_config = {
                    'host': os.environ.get('DB_HOST', 'infinityai-prod-db.mysql.database.azure.com'),
                    'user': os.environ.get('DB_USER', 'defaultuser'),
                    'password': os.environ.get('DB_PASSWORD', ''),
                    'database': os.environ.get('DB_NAME', 'infinityai'),
                    'ssl_ca': os.environ.get('DB_SSL_CA', ''),
                    'ssl_verify_cert': os.environ.get('DB_SSL_VERIFY', 'true').lower() == 'true',
                    'ssl_disabled': True,  # Disable SSL to avoid certificate issues in container
                }
                
                # Log sanitized connection info (no password)
                safe_config = {k: v for k, v in db_config.items() if k != 'password'}
                logger.info(f"Initializing database connection pool with config: {safe_config}")
                
                # Create the connection pool
                self._pool = MySQLConnectionPool(
                    pool_name="infinityai_pool",
                    pool_size=pool_size,
                    **db_config
                )
                
                # Test connection
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                
                logger.info("Database connection pool initialized successfully")
                return
            
            except Error as e:
                logger.error(f"Database connection attempt {attempt+1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.critical(f"Failed to initialize database pool after {max_retries} attempts")
                    raise
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            return False
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool with context management."""
        conn = None
        try:
            conn = self._pool.get_connection()
            yield conn
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute an update query and return the number of affected rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount

# Singleton instance
db = DatabaseManager()