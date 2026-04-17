import pymysql
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MySQLManager:
    """
    Manager class for MySQL database operations using PyMySQL.
    PyMySQL is a pure Python MySQL driver that's more stable than mysql-connector-python.
    """

    def __init__(self, host: str, user: str, password: str, default_database: Optional[str] = None):
        """
        Initialize the connection to MySQL server.
        :param host: MySQL server host
        :param user: MySQL username
        :param password: MySQL password
        :param default_database: Optional default database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.default_database = default_database
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL server."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=None,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30
            )
            logger.info("MySQL connection established with PyMySQL.")
        except Exception as e:
            logger.error(f"Error connecting to MySQL: {e}")
            self.connection = None

    def close(self):
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("MySQL connection closed.")
            except Exception as e:
                logger.error(f"Error closing MySQL connection: {e}")
        self.connection = None

    def _check_connection(self):
        """Check if connection is available, attempt to reconnect if lost."""
        try:
            if not self.connection:
                logger.warning("Connection is None, reconnecting...")
                self.close()  # Ensure cleanup
                self.connect()
                if not self.connection:
                    raise ValueError("Failed to reconnect to database")
            else:
                # Test connection with a simple ping
                try:
                    self.connection.ping()
                    logger.debug("Connection ping successful")
                except (pymysql.OperationalError, pymysql.InternalError, OSError) as e:
                    logger.warning(f"Connection ping failed ({type(e).__name__}), reconnecting...")
                    self.close()
                    self.connect()
                    if not self.connection:
                        raise ValueError("Failed to reconnect to database after ping failure")
                except Exception as e:
                    # For any other unexpected error during ping, close and reconnect
                    logger.warning(f"Unexpected error during ping: {e}, reconnecting...")
                    self.close()
                    self.connect()
                    if not self.connection:
                        raise ValueError("Failed to reconnect to database")
            
            # Select the database once after connection is verified
            target_db = self.default_database
            if target_db:
                try:
                    cursor = self.connection.cursor()
                    cursor.execute(f"USE {target_db}")
                    cursor.close()
                except Exception as e:
                    logger.warning(f"Failed to select database {target_db}: {e}")
                    
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            raise ValueError("Database connection is not available.")

    # ==================== DATABASE MANAGEMENT ====================

    def create_database(self, db_name: str):
        """Create a new database if it does not exist."""
        try:
            self._check_connection()
            cursor = self.connection.cursor()
            try:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                self.connection.commit()
                logger.info(f"Database '{db_name}' created or already exists.")
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error creating database '{db_name}': {e}")

    def delete_database(self, db_name: str):
        """Drop the specified database if it exists."""
        try:
            self._check_connection()
            cursor = self.connection.cursor()
            try:
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                self.connection.commit()
                logger.info(f"Database '{db_name}' deleted successfully.")
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error deleting database '{db_name}': {e}")

    def clear_database(self, db_name: str):
        """Remove all data from the database by truncating tables."""
        try:
            self._check_connection()
            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {db_name}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute("TRUNCATE TABLE products")
                cursor.execute("TRUNCATE TABLE categories")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                self.connection.commit()
                logger.info(f"Database '{db_name}' cleared successfully.")
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error clearing database '{db_name}': {e}")

    def create_tables_if_not_exist(self, db_name: Optional[str] = None):
        """Create the categories and products tables if they don't exist."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to create tables.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        description TEXT NULL,
                        PRIMARY KEY (id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                        name VARCHAR(200) NOT NULL,
                        description TEXT NULL,
                        category_id INT UNSIGNED NOT NULL,
                        unit VARCHAR(20) NOT NULL DEFAULT 'pcs',
                        stock_quantity DECIMAL(10,3) NOT NULL DEFAULT 0.000,
                        selling_price DECIMAL(10,2) NOT NULL,
                        is_active TINYINT(1) NOT NULL DEFAULT 1,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (id),
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE CASCADE,
                        INDEX idx_category (category_id),
                        INDEX idx_name (name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                self.connection.commit()
                logger.info(f"Tables created successfully in database '{target_db}'.")
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    # ==================== CATEGORY OPERATIONS ====================

    def create_category(self, name: str, description: Optional[str] = None,
                        db_name: Optional[str] = None) -> int:
        """Create a new category."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to create category.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)",
                    (name, description)
                )
                self.connection.commit()
                category_id = cursor.lastrowid
                logger.info(f"Category '{name}' created with id {category_id}.")
                return category_id
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise

    def get_category(self, category_id: int, db_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve a category by id."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to get category.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute("SELECT id, name, description FROM categories WHERE id = %s", (category_id,))
                return cursor.fetchone()
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error retrieving category: {e}")
            raise

    def get_all_categories(self, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all categories."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to get categories.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute("SELECT id, name, description FROM categories ORDER BY name ASC")
                return cursor.fetchall() or []
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            raise

    def update_category(self, category_id: int, name: Optional[str] = None,
                        description: Optional[str] = None, db_name: Optional[str] = None) -> bool:
        """Update a category."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to update category.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                updates = []
                params = []

                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)

                if not updates:
                    return False

                params.append(category_id)
                query = f"UPDATE categories SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(query, params)
                self.connection.commit()

                return cursor.rowcount > 0
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            raise

    def delete_category(self, category_id: int, db_name: Optional[str] = None) -> bool:
        """Delete a category."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to delete category.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
                self.connection.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            raise

    # ==================== PRODUCT OPERATIONS ====================

    def create_product(self, name: str, category_id: int, unit: str = 'pcs',
                       stock_quantity: float = 0.0, selling_price: float = 0.0,
                       description: Optional[str] = None, is_active: int = 1,
                       db_name: Optional[str] = None) -> int:
        """Create a new product."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to create product.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute(
                    """INSERT INTO products (name, description, category_id, unit, stock_quantity, 
                       selling_price, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (name, description, category_id, unit, stock_quantity, selling_price, is_active)
                )
                self.connection.commit()
                product_id = cursor.lastrowid
                logger.info(f"Product '{name}' created with id {product_id}.")
                return product_id
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise

    def get_product(self, product_id: int, db_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve a product by id."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to get product.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute(
                    """SELECT id, name, description, category_id, unit, stock_quantity, 
                       selling_price, is_active, created_at, updated_at FROM products WHERE id = %s""",
                    (product_id,)
                )
                return cursor.fetchone()
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error retrieving product: {e}")
            raise

    def get_all_products(self, category_id: Optional[int] = None, is_active: Optional[int] = None,
                         db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve products with optional filtering."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to get products.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                query = """SELECT id, name, description, category_id, unit, stock_quantity, 
                           selling_price, is_active, created_at, updated_at FROM products WHERE 1=1"""
                params = []

                if category_id is not None:
                    query += " AND category_id = %s"
                    params.append(category_id)
                if is_active is not None:
                    query += " AND is_active = %s"
                    params.append(is_active)

                query += " ORDER BY name ASC"

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                return cursor.fetchall() or []
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            raise

    def update_product(self, product_id: int, name: Optional[str] = None,
                       description: Optional[str] = None, category_id: Optional[int] = None,
                       unit: Optional[str] = None, stock_quantity: Optional[float] = None,
                       selling_price: Optional[float] = None, is_active: Optional[int] = None,
                       db_name: Optional[str] = None) -> bool:
        """Update a product."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to update product.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                updates = []
                params = []

                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                if category_id is not None:
                    updates.append("category_id = %s")
                    params.append(category_id)
                if unit is not None:
                    updates.append("unit = %s")
                    params.append(unit)
                if stock_quantity is not None:
                    updates.append("stock_quantity = %s")
                    params.append(stock_quantity)
                if selling_price is not None:
                    updates.append("selling_price = %s")
                    params.append(selling_price)
                if is_active is not None:
                    updates.append("is_active = %s")
                    params.append(is_active)

                if not updates:
                    return False

                params.append(product_id)
                query = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(query, params)
                self.connection.commit()

                return cursor.rowcount > 0
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            raise

    def delete_product(self, product_id: int, db_name: Optional[str] = None) -> bool:
        """Delete a product."""
        try:
            self._check_connection()
            target_db = db_name or self.default_database
            if not target_db:
                raise ValueError("No database specified to delete product.")

            cursor = self.connection.cursor()
            try:
                cursor.execute(f"USE {target_db}")
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                self.connection.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            raise
