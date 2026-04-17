import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MySQLManager:
    """
    Manager class for MySQL database operations for Grocery Assistant.
    Handles database creation, table setup, and CRUD for categories and products.
    """

    def __init__(self, host: str, user: str, password: str, default_database: Optional[str] = None):
        """
        Initialize the connection to MySQL server (without a default database).
        :param host: MySQL server host
        :param user: MySQL username
        :param password: MySQL password
        :param default_database: Optional default database name to use when not specified in methods
        """
        self.host = host
        self.user = user
        self.password = password
        self.default_database = default_database
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL server (no database selected)."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=None  
            )
            logger.info("MySQL connection established.")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            self.connection = None

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
                logger.info("MySQL connection closed.")
            except Error as e:
                logger.error(f"Error closing MySQL connection: {e}")
        self.connection = None

    def _check_connection(self):
        """Check if connection is available, raise ValueError if not."""
        if not self.connection or not self.connection.is_connected():
            raise ValueError("Database connection is not available. Ensure MySQL server is running and credentials are correct.")



    def create_database(self, db_name: str):
        """
        Create a new database with the given name if it does not exist.
        Uses utf8mb4 character set for full Unicode support.
        """
        try:
            self._check_connection()
        except ValueError as e:
            logger.error(str(e))
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} "
                           f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self.connection.commit()
            logger.info(f"Database '{db_name}' created or already exists.")
        except Error as e:
            logger.error(f"Error creating database '{db_name}': {e}")
        finally:
            cursor.close()

    def delete_database(self, db_name: str):
        """Drop the specified database if it exists."""
        try:
            self._check_connection()
        except ValueError as e:
            logger.error(str(e))
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            self.connection.commit()
            logger.info(f"Database '{db_name}' deleted successfully.")
        except Error as e:
            logger.error(f"Error deleting database '{db_name}': {e}")
        finally:
            cursor.close()

    def clear_database(self, db_name: str):
        """
        Remove all data from the database by truncating products and categories tables.
        The database itself is not deleted.
        """
        try:
            self._check_connection()
        except ValueError as e:
            logger.error(str(e))
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {db_name}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("TRUNCATE TABLE products")
            cursor.execute("TRUNCATE TABLE categories")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            logger.info(f"Database '{db_name}' cleared successfully.")
        except Error as e:
            logger.error(f"Error clearing database '{db_name}': {e}")
        finally:
            cursor.close()


    def create_tables_if_not_exist(self, db_name: Optional[str] = None):
        """
        Create the `categories` and `products` tables in the specified database.
        If db_name is omitted, self.default_database is used.
        """
        try:
            self._check_connection()
        except ValueError as e:
            logger.error(str(e))
            return

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
                    unit VARCHAR(20) NOT NULL DEFAULT 'pcs' COMMENT 'e.g., kg, g, l, pcs, pack',
                    stock_quantity DECIMAL(10,3) NOT NULL DEFAULT 0.000 COMMENT 'Current quantity on hand',
                    selling_price DECIMAL(10,2) NOT NULL COMMENT 'Retail price per unit',
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
        except Error as e:
            logger.error(f"Error creating tables: {e}")
        finally:
            cursor.close()

    # ==================== CATEGORY OPERATIONS ====================

    def create_category(self, name: str, description: Optional[str] = None,
                        db_name: Optional[str] = None) -> int:
        """
        Create a new category.
        :param name: category name (unique)
        :param description: optional category description
        :param db_name: target database; if None, self.default_database is used
        :return: the id of the created category
        """
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
            print(f"Category '{name}' created with id {category_id}.")
            return category_id
        finally:
            cursor.close()

    def get_category(self, category_id: int, db_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a category by id.
        :param category_id: the category id
        :param db_name: target database; if None, self.default_database is used
        :return: category record as dict or None if not found
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to get category.")

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute("SELECT id, name, description FROM categories WHERE id = %s", (category_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_all_categories(self, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all categories.
        :param db_name: target database; if None, self.default_database is used
        :return: list of category records
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to get categories.")

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute("SELECT id, name, description FROM categories ORDER BY name ASC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def update_category(self, category_id: int, name: Optional[str] = None,
                        description: Optional[str] = None, db_name: Optional[str] = None) -> bool:
        """
        Update a category.
        :param category_id: the category id
        :param name: new category name (optional)
        :param description: new category description (optional)
        :param db_name: target database; if None, self.default_database is used
        :return: True if update was successful, False if category not found
        """
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

            if cursor.rowcount > 0:
                print(f"Category with id {category_id} updated.")
                return True
            return False
        finally:
            cursor.close()

    def delete_category(self, category_id: int, db_name: Optional[str] = None) -> bool:
        """
        Delete a category (will fail if products reference it).
        :param category_id: the category id
        :param db_name: target database; if None, self.default_database is used
        :return: True if deletion was successful, False if category not found
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to delete category.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            self.connection.commit()

            if cursor.rowcount > 0:
                print(f"Category with id {category_id} deleted.")
                return True
            return False
        finally:
            cursor.close()

    # ==================== PRODUCT OPERATIONS ====================

    def create_product(self, name: str, category_id: int, unit: str = 'pcs',
                       stock_quantity: float = 0.0, selling_price: float = 0.0,
                       description: Optional[str] = None, is_active: int = 1,
                       db_name: Optional[str] = None) -> int:
        """
        Create a new product.
        :param name: product name
        :param category_id: category id
        :param unit: unit of measurement (default: 'pcs')
        :param stock_quantity: initial stock quantity (default: 0)
        :param selling_price: selling price per unit
        :param description: optional product description
        :param is_active: 1 for active, 0 for inactive (default: 1)
        :param db_name: target database; if None, self.default_database is used
        :return: the id of the created product
        """
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
            print(f"Product '{name}' created with id {product_id}.")
            return product_id
        finally:
            cursor.close()

    def get_product(self, product_id: int, db_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a product by id.
        :param product_id: the product id
        :param db_name: target database; if None, self.default_database is used
        :return: product record as dict or None if not found
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to get product.")

        cursor = self.connection.cursor(dictionary=True)
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

    def get_all_products(self, category_id: Optional[int] = None, is_active: Optional[int] = None,
                         db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve products with optional filtering.
        :param category_id: filter by category id (optional)
        :param is_active: filter by active status (optional)
        :param db_name: target database; if None, self.default_database is used
        :return: list of product records
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to get products.")

        cursor = self.connection.cursor(dictionary=True)
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

            return cursor.fetchall()
        finally:
            cursor.close()

    def update_product(self, product_id: int, name: Optional[str] = None,
                       description: Optional[str] = None, category_id: Optional[int] = None,
                       unit: Optional[str] = None, stock_quantity: Optional[float] = None,
                       selling_price: Optional[float] = None, is_active: Optional[int] = None,
                       db_name: Optional[str] = None) -> bool:
        """
        Update a product.
        :param product_id: the product id
        :param name: new product name (optional)
        :param description: new product description (optional)
        :param category_id: new category id (optional)
        :param unit: new unit (optional)
        :param stock_quantity: new stock quantity (optional)
        :param selling_price: new selling price (optional)
        :param is_active: new active status (optional)
        :param db_name: target database; if None, self.default_database is used
        :return: True if update was successful, False if product not found
        """
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

            if cursor.rowcount > 0:
                print(f"Product with id {product_id} updated.")
                return True
            return False
        finally:
            cursor.close()

    def delete_product(self, product_id: int, db_name: Optional[str] = None) -> bool:
        """
        Delete a product.
        :param product_id: the product id
        :param db_name: target database; if None, self.default_database is used
        :return: True if deletion was successful, False if product not found
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to delete product.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            self.connection.commit()

            if cursor.rowcount > 0:
                print(f"Product with id {product_id} deleted.")
                return True
            return False
        finally:
            cursor.close()