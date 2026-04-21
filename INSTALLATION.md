# 🚀 Grocery Assistant - Installation Guide

Complete step-by-step guide to set up and run the Grocery Assistant application.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Database Setup](#database-setup)
4. [Running the Application](#running-the-application)
5. [Verification](#verification)
6. [Common Issues](#common-issues)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **MySQL**: 5.7 or higher (8.0+ recommended)
- **RAM**: 2GB minimum
- **Disk Space**: 500MB free

### Recommended Setup
- **Python**: 3.10 or higher
- **MySQL**: 8.0 or higher
- **RAM**: 4GB or more
- **SSD**: 1GB free space

---

## Installation Steps

### 1. Check Your System

```bash
# Check Python version
python3 --version
# Expected output: Python 3.8.x or higher

# Check pip version
pip3 --version
# Expected output: pip 20.x or higher

# Check if MySQL is installed
mysql --version
# Expected output: mysql  Ver 8.x.x or higher
```

If any of these are missing, install them:

**macOS (using Homebrew):**
```bash
brew install python3
brew install mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip mysql-server
```

**Windows:**
- Download Python from https://www.python.org/
- Download MySQL from https://dev.mysql.com/downloads/mysql/

---

### 2. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Sethuram2003/GroceryAssistant.git

# Navigate to project directory
cd GroceryAssistant

# List contents to verify
ls -la
```

Expected directory structure:
```
GroceryAssistant/
├── app/
├── static/
├── requirements.txt
├── README.md
└── ...
```

---

### 3. Create Virtual Environment

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your terminal)
which python
```

**Windows (Command Prompt):**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (you should see (venv) in your terminal)
where python
```

**Windows (PowerShell):**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 4. Install Python Dependencies

```bash
# Ensure virtual environment is activated
# (You should see (venv) at the beginning of your terminal prompt)

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -i fastapi
pip list | grep -i mysql
```

**Expected packages:**
- fastapi
- uvicorn
- mysql-connector-python
- python-dotenv

---

### 5. Set Up MySQL Database

#### Start MySQL Server

**macOS (Homebrew):**
```bash
# Start MySQL service
brew services start mysql

# Verify MySQL is running
mysql -u root -e "SELECT 1;"
```

**Linux (Systemd):**
```bash
# Start MySQL service
sudo systemctl start mysql

# Verify MySQL is running
sudo systemctl status mysql
```

**Windows:**
```bash
# MySQL usually starts automatically
# Verify it's running
mysql -u root -p -e "SELECT 1;"
```

#### Create Database and User

```bash
# Connect to MySQL (will prompt for password)
mysql -u root -p

# You'll see the MySQL prompt: mysql>
```

Then execute these SQL commands:

```sql
-- Create database
CREATE DATABASE grocery_db;

-- Create user
CREATE USER 'grocery_user'@'localhost' IDENTIFIED BY 'grocery_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON grocery_db.* TO 'grocery_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify setup
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user = 'grocery_user';

-- Exit MySQL
EXIT;
```

#### Create Tables

```bash
# Connect to your new database with the new user
mysql -u grocery_user -p grocery_db
# Password: grocery_password
```

Then execute:

```sql
-- Create categories table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create products table
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
    INDEX idx_active (is_active),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify tables
SHOW TABLES;

-- Exit
EXIT;
```

---

### 6. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your preferred editor
nano .env
# or
vim .env
# or open it in your IDE
```

Update the values:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=grocery_user
MYSQL_PASSWORD=grocery_password
MYSQL_DATABASE=grocery_db
API_PORT=8000
API_HOST=0.0.0.0
ENVIRONMENT=development
DEBUG=True
```

**Save and close the file.**

---

## Running the Application

### Step 1: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 2: Verify Setup

```bash
# Check Python path (should point to venv)
which python
# or
where python

# Check MySQL connection
mysql -u grocery_user -p -e "SELECT 1;"
# Password: grocery_password
```

### Step 3: Start the FastAPI Server

**Development Mode (with auto-reload):**
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Access the Application

Open your web browser and go to:

```
http://localhost:8000
```

You should see the Grocery Assistant interface!

---

## Verification

### Check API Health

```bash
# In a new terminal, run:
curl http://localhost:8000/health/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Grocery Assistant API is running"
}
```

### Check Database Connection

```bash
# Check if categories table has any data
mysql -u grocery_user -p grocery_db -e "SELECT * FROM categories;"
```

### Access API Documentation

Visit in your browser:
```
http://localhost:8000/docs
```

You should see the interactive Swagger API documentation.

---

## Common Issues

### Issue: "Can't connect to MySQL server"

**Solution:**
```bash
# Check if MySQL is running
mysql -u root -e "SELECT 1;"

# If not running, start it
brew services start mysql  # macOS
sudo systemctl start mysql  # Linux
```

### Issue: "Module 'fastapi' not found"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 8000 is already in use"

**Solution:**
```bash
# Find and kill the process (macOS/Linux)
lsof -i :8000
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001 --reload
```

### Issue: "Access denied for user 'grocery_user'"

**Solution:**
```bash
# Check .env file for correct credentials
cat .env | grep MYSQL

# Re-create the MySQL user if needed
mysql -u root -p
# Then run the SQL commands from the Database Setup section
```

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
# Ensure you're in the correct directory
pwd  # Should show: .../GroceryAssistant

# Run from the project root directory
cd /path/to/GroceryAssistant
uvicorn app.main:app --reload
```

---

## Next Steps

1. **Import Sample Data**: Use the CSV import feature to add some test products
2. **Explore Features**: Try all tabs - Categories, Products, Chat, etc.
3. **Test API**: Visit `/docs` for interactive API testing
4. **Check Logs**: Monitor terminal output for any issues

---

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) for more information
2. Review the Troubleshooting section in README
3. Check the terminal output for error messages
4. Search existing GitHub issues
5. Create a new issue with details and error logs

---

**Happy coding! 🚀**
