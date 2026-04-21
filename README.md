# 🛒 Grocery Assistant

A modern, full-stack web application for managing grocery store inventory, products, and categories with an intelligent AI chatbot assistant. Built with **FastAPI** backend and a beautiful responsive frontend with real-time filtering and CSV import capabilities.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [CSV Import Guide](#csv-import-guide)
- [Features Guide](#features-guide)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ✨ Features

### 🎯 Core Features

- **📁 Category Management**
  - Create, read, update, and delete product categories
  - View product counts per category
  - Click on categories to filter products instantly

- **📦 Product Management**
  - Full CRUD operations for products
  - Track stock quantities, prices, and availability status
  - Link products to categories
  - Filter products by category, search term, or status

- **📥 CSV Import**
  - Bulk import products and categories from CSV files
  - Real-time CSV validation with detailed error reporting
  - Download CSV templates
  - Progress tracking during import
  - Import success summary with error logging

- **📊 Dashboard**
  - Real-time statistics (total categories, products, stock value)
  - Quick overview of active products
  - Recent products display

- **💬 AI Chat Assistant**
  - Intelligent chatbot for grocery-related queries
  - Real-time chat interface
  - Markdown support for rich responses
  - Conversation history

- **🔍 Advanced Filtering**
  - Search products by name
  - Filter by category
  - Filter by active/inactive status
  - Real-time filter updates

- **💾 Database Connection Status**
  - Real-time connection indicator
  - Visual feedback for database availability

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MySQL
- **ORM**: MySQL Python Connector
- **Async**: AsyncIO
- **Documentation**: Automatic OpenAPI/Swagger documentation

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Vanilla ES6+ (no frameworks)
- **Libraries**: 
  - Marked.js (Markdown parsing)
  - Native Fetch API (HTTP requests)

### DevTools
- **API Testing**: curl/Postman compatible
- **Package Management**: pip (Python)

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
  ```bash
  python3 --version
  ```
- **MySQL Server 5.7 or higher** (or MySQL 8.0+)
  ```bash
  mysql --version
  ```
- **pip** (Python package manager)
  ```bash
  pip --version
  ```
- **Git**
  ```bash
  git --version
  ```

### System Requirements

- RAM: Minimum 2GB (4GB recommended)
- Disk Space: At least 500MB free
- Port Availability: 8000 (FastAPI), 3306 (MySQL)

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sethuram2003/GroceryAssistant.git
cd GroceryAssistant
```

### Step 2: Create a Python Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

The main dependencies include:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `mysql-connector-python` - MySQL database connector
- `python-dotenv` - Environment variable management

### Step 4: Database Setup

#### Option A: Using MySQL Command Line

1. **Start MySQL Server**
   ```bash
   # macOS (if installed via Homebrew)
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   
   # Windows
   net start MySQL80  # or your MySQL version
   ```

2. **Create Database and User**
   ```bash
   mysql -u root -p
   ```
   
   Then run these SQL commands:
   ```sql
   CREATE DATABASE grocery_db;
   CREATE USER 'grocery_user'@'localhost' IDENTIFIED BY 'grocery_password';
   GRANT ALL PRIVILEGES ON grocery_db.* TO 'grocery_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. **Create Tables**
   
   The application will automatically create the necessary tables when it first runs. However, you can manually create them using the following SQL:

   ```sql
   USE grocery_db;

   CREATE TABLE categories (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(255) NOT NULL UNIQUE,
       description TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );

   CREATE TABLE products (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       description TEXT,
       category_id INT NOT NULL,
       unit VARCHAR(50),
       stock_quantity DECIMAL(10, 3),
       selling_price DECIMAL(10, 2),
       is_active TINYINT(1) DEFAULT 1,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
       INDEX idx_category (category_id),
       INDEX idx_active (is_active)
   );
   ```

### Step 5: Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env  # if available
```

Or create a new `.env` file:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=grocery_user
MYSQL_PASSWORD=grocery_password
MYSQL_DATABASE=grocery_db

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Environment
ENVIRONMENT=development
DEBUG=True

# AI/Chat Configuration (if using AI features)
OPENAI_API_KEY=your_api_key_here  # Optional
```

### Step 6: Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Test if dependencies are installed
python -c "import fastapi, mysql.connector; print('✅ Dependencies installed successfully')"
```

## 📁 Project Structure

```
GroceryAssistant/
├── app/                                 # Main application package
│   ├── __init__.py
│   ├── main.py                         # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/                     # API route handlers
│   │       ├── __init__.py
│   │       ├── healthcheck.py          # Health check endpoint
│   │       ├── categories.py           # Category CRUD operations
│   │       ├── products.py             # Product CRUD operations
│   │       ├── import_csv.py           # CSV import functionality
│   │       └── chat.py                 # Chat/AI assistant endpoint
│   └── core/
│       ├── __init__.py
│       ├── agent.py                    # AI agent logic
│       ├── prompts.py                  # AI prompt templates
│       └── mysql_database/
│           ├── __init__.py
│           ├── mysql_manager.py        # Database manager class
│           └── mysql_service.py        # Database service layer
├── static/                              # Frontend files
│   ├── index.html                      # Main HTML file
│   ├── script.js                       # JavaScript logic
│   └── style.css                       # Styling
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (create this)
├── README.md                           # This file
└── LICENSE                             # License file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=grocery_user
MYSQL_PASSWORD=grocery_password
MYSQL_DATABASE=grocery_db

# API Server
API_PORT=8000
API_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO

# Features
ENABLE_CHAT=true
ENABLE_CSV_IMPORT=true
```

### Database Connection

The application uses a connection pool to manage MySQL connections efficiently. Connection details are configured in `app/core/mysql_database/mysql_service.py`.

## ▶️ Running the Application

### Step 1: Activate Virtual Environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 2: Ensure MySQL is Running

```bash
# Check MySQL status
mysql -u root -p -e "SELECT 1;"
```

### Step 3: Start the FastAPI Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode (no auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete
```

### Step 4: Access the Application

Open your web browser and navigate to:

```
http://localhost:8000/
```

## 🔌 API Endpoints

### Health Check
- **GET** `/health/`
  - Check API and database status
  - Response: `{ "status": "healthy", "message": "..." }`

### Categories

- **GET** `/categories/`
  - List all categories
  - Response: Array of category objects

- **POST** `/categories/`
  - Create a new category
  - Body: `{ "name": "string", "description": "string" }`

- **PUT** `/categories/{id}`
  - Update a category
  - Body: `{ "name": "string", "description": "string" }`

- **DELETE** `/categories/{id}`
  - Delete a category

### Products

- **GET** `/products/`
  - List all products
  - Response: Array of product objects

- **POST** `/products/`
  - Create a new product
  - Body:
    ```json
    {
      "name": "string",
      "description": "string",
      "category_id": 1,
      "unit": "kg",
      "stock_quantity": 10.5,
      "selling_price": 5.99,
      "is_active": 1
    }
    ```

- **PUT** `/products/{id}`
  - Update a product

- **DELETE** `/products/{id}`
  - Delete a product

### CSV Import

- **POST** `/api/import-csv`
  - Import products and categories from CSV file
  - Content-Type: multipart/form-data
  - File parameter: `file` (CSV file)

- **POST** `/api/import-csv/validate`
  - Validate CSV file without importing
  - Content-Type: multipart/form-data
  - Returns: Validation results and errors

- **GET** `/api/import-csv/template`
  - Download CSV template

### Chat

- **POST** `/chat/`
  - Send a message to the AI assistant
  - Body: `{ "message": "string" }`

## 📊 CSV Import Guide

### CSV Format

The CSV file must have the following columns in order:

| Column | Type | Required | Example |
|--------|------|----------|---------|
| category_name | Text | Yes | Fruits |
| category_description | Text | Yes | Fresh seasonal fruits |
| product_name | Text | Yes | Apple |
| product_description | Text | Yes | Red delicious apples |
| unit | Text | Yes | kg |
| stock_quantity | Decimal | Yes | 25.5 |
| selling_price | Decimal | Yes | 3.99 |
| is_active | Integer (0/1) | Yes | 1 |

### Sample CSV File

```csv
category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Fruits,Fresh and seasonal fruits,Apple,Red delicious apples,kg,25.5,3.99,1
Fruits,Fresh and seasonal fruits,Banana,Ripe Cavendish bananas,kg,40.2,2.49,1
Vegetables,Organic and locally grown vegetables,Tomato,Vine-ripened tomatoes,kg,32.0,3.79,1
Dairy,Milk and dairy products,Milk 2%,2% reduced fat milk,l,120.0,3.49,1
Beverages,Soft drinks and juices,Orange Juice,Fresh orange juice,l,35.0,4.99,1
```

### How to Import

1. Go to **📥 Import CSV** tab
2. Click **Browse Files** or drag and drop a CSV file
3. Click **✓ Validate CSV** to check for errors
4. If valid, click **🚀 Import Data to Database**
5. Monitor the progress and review results

## 🎨 Features Guide

### Dashboard Tab 📊
- View key statistics at a glance
- See total categories, products, and stock value
- Monitor product status

### Categories Tab 📁
- View all product categories
- Create new categories with names and descriptions
- Click on any category to filter products
- Edit or delete categories

### Products Tab 📦
- Browse all products in a table format
- Search products by name
- Filter by category or active status
- View product details (price, stock, unit)
- Create, edit, or delete products

### Import CSV Tab 📥
- Upload CSV files with product data
- Validate CSV format before importing
- Track import progress
- View import results and any errors
- Download CSV template for reference

### Chat Tab 💬
- Chat with AI assistant
- Get grocery-related recommendations
- Real-time responses
- Clean conversation interface

## 🐛 Troubleshooting

### MySQL Connection Issues

**Error**: `Can't connect to MySQL server`

**Solutions**:
1. Check if MySQL is running:
   ```bash
   mysql -u root -p -e "SELECT 1;"
   ```
2. Verify credentials in `.env` file
3. Check MySQL port (default: 3306)
4. Ensure database and user exist:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

### Port Already in Use

**Error**: `Address already in use`

**Solutions**:
1. Kill the process using port 8000:
   ```bash
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. Run on a different port:
   ```bash
   uvicorn app.main:app --port 8001
   ```

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### CSV Import Validation Errors

**Error**: `Missing required columns`

**Solutions**:
1. Download the CSV template from the app
2. Ensure column names match exactly
3. Check data types (numbers for numeric columns)
4. Review error messages in validation results

### Slow Performance

**Solutions**:
1. Check MySQL indexing
2. Monitor database connection pool
3. Check system resources (CPU, RAM, disk)
4. Review API logs for bottlenecks

## 📝 API Documentation

Once the server is running, visit:

```
http://localhost:8000/docs
```

This provides an interactive Swagger UI where you can:
- View all available endpoints
- Test API calls directly
- See request/response examples
- Download OpenAPI schema

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Author

**Sethuram** - [GitHub Profile](https://github.com/Sethuram2003)

## 📞 Support

For issues and questions:

1. Check the Troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include error messages and steps to reproduce

## 🎯 Roadmap

- [ ] User authentication and roles
- [ ] Advanced analytics and reporting
- [ ] Mobile app (React Native)
- [ ] Real-time notifications
- [ ] Barcode scanning
- [ ] Inventory alerts
- [ ] Multi-store support
- [ ] API rate limiting

## 🙏 Acknowledgments

- FastAPI documentation and community
- MySQL community
- All contributors and users

---

**Last Updated**: April 2026
**Version**: 1.0.0
