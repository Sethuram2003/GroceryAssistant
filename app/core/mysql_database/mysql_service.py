import os
import logging
from app.core.mysql_database.mysql_manager import MySQLManager
import atexit
import threading

logger = logging.getLogger(__name__)
mysql_service = None
_db_initialized = False
_lock = threading.RLock()  # Reentrant lock for double-locking singleton pattern

def get_mysql_service() -> MySQLManager:
    """
    FastAPI dependency to get the MySQL service instance using double-locking singleton pattern.
    This ensures thread-safe, lazy initialization of the database connection.
    
    Double-locking pattern:
    1. First check without lock (fast path for subsequent calls)
    2. If needed, acquire lock and check again (slow path for initialization)
    3. This avoids lock contention on every request after initialization
    """
    global mysql_service
    global _db_initialized
    
    # First check without lock (fast path)
    if mysql_service is not None:
        try:
            # Verify connection is still healthy
            if mysql_service.connection:
                try:
                    mysql_service.connection.ping()
                    logger.debug("Connection healthy, returning existing service")
                    return mysql_service
                except Exception as e:
                    logger.warning(f"Connection ping failed: {e}, will reconnect...")
        except Exception as e:
            logger.warning(f"Error checking connection: {e}")
    
    # Slow path: acquire lock for initialization or reconnection
    with _lock:
        # Double-check after acquiring lock
        if mysql_service is not None:
            try:
                if mysql_service.connection:
                    try:
                        mysql_service.connection.ping()
                        logger.debug("Connection verified after lock acquisition")
                        return mysql_service
                    except Exception:
                        logger.warning("Reconnecting due to failed ping...")
                        mysql_service.close()
            except Exception as e:
                logger.warning(f"Error during double-check: {e}")
        
        # Initialize or reinitialize the service
        try:
            logger.info("Creating/reconnecting MySQL service...")
            mysql_service = MySQLManager(
                host=os.getenv("MYSQL_HOST", "localhost"),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                default_database=os.getenv("MYSQL_DATABASE", "grocery_shop")  
            )

            if not mysql_service.connection:
                logger.error("MySQL connection object creation failed")
                mysql_service = None
                raise ValueError("Failed to create MySQL connection")
            
            # Initialize database schema (only once)
            db_name = os.getenv("MYSQL_DATABASE")
            if db_name and not _db_initialized:
                try:
                    mysql_service.create_database(db_name)
                    mysql_service.create_tables_if_not_exist(db_name)
                    logger.info(f"Database '{db_name}' initialized successfully")
                    _db_initialized = True
                except Exception as e:
                    logger.error(f"Error initializing database: {e}")
                    # Don't fail - allow API to function even if init fails
            
            # Register cleanup (only on initial creation)
            if _db_initialized:
                atexit.register(close_mysql_service)
            
            logger.info("MySQL service ready")
            return mysql_service
            
        except Exception as e:
            logger.error(f"Failed to initialize MySQL service: {e}", exc_info=True)
            mysql_service = None
            raise




def close_mysql_service():
    """Close the MySQL service connection (for application shutdown)."""
    global mysql_service
    if mysql_service:
        try:
            logger.info("Closing MySQL connection...")
            mysql_service.close()
            logger.info("MySQL service closed successfully")
        except Exception as e:
            logger.error(f"Error closing MySQL service: {e}")
        finally:
            mysql_service = None