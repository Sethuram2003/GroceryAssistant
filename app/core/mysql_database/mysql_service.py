import os
from app.core.mysql_database.mysql_manager import MySQLManager

mysql_service = None

def get_mysql_service() -> MySQLManager:
    """
    FastAPI dependency to get or create the MySQL service instance.
    The instance is created once and reused for subsequent calls.
    """
    global mysql_service

    if mysql_service is None:
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

    return mysql_service


def close_mysql_service():
    """Close the MySQL service connection (for application shutdown)."""
    global mysql_service
    if mysql_service:
        mysql_service.close()
        mysql_service = None