import os
import logging
from app.core.mysql_database.mysql_manager import MySQLManager
import atexit
import threading
from typing import Generator

logger = logging.getLogger(__name__)
_db_initialized = False
_lock = threading.RLock()

def get_mysql_service() -> Generator[MySQLManager, None, None]:
    """
    FastAPI dependency that yields a fresh MySQL connection per request and closes it after.
    
    Uses double-locking pattern for one-time database schema initialization.
    Creates fresh connections to avoid staleness and corruption issues.
    
    Usage in routes:
        @router.get("/")
        def my_endpoint(db: MySQLManager = Depends(get_mysql_service)):
            ...
    """
    global _db_initialized
    
    if not _db_initialized:
        with _lock:
            if not _db_initialized:
                try:
                    logger.info("Initializing database schema...")
                    temp_service = MySQLManager(
                        host=os.getenv("MYSQL_HOST", "localhost"),
                        user=os.getenv("MYSQL_USER", "root"),
                        password=os.getenv("MYSQL_PASSWORD", ""),
                        default_database=os.getenv("MYSQL_DATABASE", "grocery_shop")  
                    )
                    
                    db_name = os.getenv("MYSQL_DATABASE")
                    if db_name:
                        temp_service.create_database(db_name)
                        temp_service.create_tables_if_not_exist(db_name)
                        logger.info(f"Database '{db_name}' initialized successfully")
                    
                    temp_service.close()
                    _db_initialized = True
                    atexit.register(close_mysql_service)
                    
                except Exception as e:
                    logger.error(f"Failed to initialize database schema: {e}", exc_info=True)
                    raise
    
    service = None
    try:
        service = MySQLManager(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            default_database=os.getenv("MYSQL_DATABASE", "grocery_shop")  
        )
        yield service
        
    except Exception as e:
        logger.error(f"Failed to create MySQL connection: {e}", exc_info=True)
        raise
    finally:
        if service:
            try:
                service.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")


def close_mysql_service():
    """Cleanup function called on application shutdown."""
    logger.info("MySQL service shutdown cleanup")