import os
import logging
from app.core.mysql_database.mysql_manager import MySQLManager

logger = logging.getLogger(__name__)
mysql_service = None

def get_mysql_service() -> MySQLManager:
    """
    FastAPI dependency to get or create the MySQL service instance.
    The instance is created once and reused for subsequent calls.
    """
    global mysql_service

    if mysql_service is None:
        try:
            mysql_service = MySQLManager(
                host=os.getenv("MYSQL_HOST", "localhost"),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                default_database=os.getenv("MYSQL_DATABASE", "grocery_shop")  
            )

            db_name = os.getenv("MYSQL_DATABASE")
            if db_name:
                mysql_service.create_database(db_name)
                mysql_service.create_tables_if_not_exist(db_name)
                logger.info(f"Database '{db_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL service: {e}")
            logger.warning("Proceeding without database connection. API will be available but database operations will fail.")
            return None

    return mysql_service


def close_mysql_service():
    """Close the MySQL service connection (for application shutdown)."""
    global mysql_service
    if mysql_service:
        try:
            mysql_service.close()
        except Exception as e:
            logger.error(f"Error closing MySQL service: {e}")
        finally:
            mysql_service = None