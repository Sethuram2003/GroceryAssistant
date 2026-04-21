# 📥 CSV Import Guide

Complete guide to importing product and category data using CSV files.

## Table of Contents
- [CSV Format](#csv-format)
- [Column Specifications](#column-specifications)
- [Sample Data](#sample-data)
- [Import Steps](#import-steps)
- [Validation Process](#validation-process)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## CSV Format

The CSV file must be a standard comma-separated values file with:
- **Encoding**: UTF-8 (recommended)
- **Line Endings**: LF (Unix) or CRLF (Windows)
- **Header Row**: Required on first line

### Required Columns (in order)

1. `category_name`
2. `category_description`
3. `product_name`
4. `product_description`
5. `unit`
6. `stock_quantity`
7. `selling_price`
8. `is_active`

---

## Column Specifications

| # | Column Name | Data Type | Required | Constraints | Example |
|---|-------------|-----------|----------|-------------|---------|
| 1 | category_name | Text | Yes | Max 255 chars, Unique per import | "Fruits" |
| 2 | category_description | Text | Yes | Max 1000 chars | "Fresh seasonal fruits" |
| 3 | product_name | Text | Yes | Max 255 chars | "Red Apples" |
| 4 | product_description | Text | Yes | Max 1000 chars | "Fresh red delicious apples" |
| 5 | unit | Text | Yes | Common: kg, g, l, ml, pcs | "kg" |
| 6 | stock_quantity | Decimal | Yes | >= 0, Max 2 decimals | "25.50" |
| 7 | selling_price | Decimal | Yes | >= 0, Max 2 decimals | "3.99" |
| 8 | is_active | Integer | Yes | 0 or 1 (0=inactive, 1=active) | "1" |

### Field Details

**category_name**
- Unique identifier for the category
- Cannot contain leading/trailing spaces
- Will be trimmed automatically
- Example: "Fruits", "Vegetables", "Dairy"

**category_description**
- Brief description of the category
- Can be empty string ("") but field must exist
- Example: "Fresh and seasonal fruits", "Organic vegetables"

**product_name**
- Name of the product
- Can be duplicate across different categories
- Example: "Apple", "Tomato", "Milk"

**product_description**
- Detailed product description
- Can be empty string ("") but field must exist
- Example: "Red delicious apples from Washington", "Vine-ripened tomatoes"

**unit**
- Unit of measurement for stock
- Common values:
  - "kg" - Kilograms
  - "g" - Grams
  - "l" - Liters
  - "ml" - Milliliters
  - "pcs" - Pieces
  - "pack" - Pack
  - "box" - Box

**stock_quantity**
- Current stock amount
- Must be a valid number
- Can include decimals (e.g., "25.5", "0.75")
- Cannot be negative
- Example: "25.50", "100", "0.5"

**selling_price**
- Price per unit in currency
- Must be a valid number
- Should include 2 decimal places
- Cannot be negative (but can be 0)
- Example: "3.99", "10.50", "0.99"

**is_active**
- Status of the product
- Integer value: 0 or 1
- 1 = Active (available for sale)
- 0 = Inactive (not available)
- Example: "1", "0"

---

## Sample Data

### Example 1: Basic Grocery Store

```csv
category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Fruits,Fresh and seasonal fruits,Apple,Red delicious apples,kg,25.5,3.99,1
Fruits,Fresh and seasonal fruits,Banana,Ripe Cavendish bananas,kg,40.2,2.49,1
Fruits,Fresh and seasonal fruits,Orange,Fresh Valencia oranges,kg,30.0,4.50,1
Vegetables,Organic and locally grown vegetables,Tomato,Vine-ripened tomatoes,kg,32.0,3.79,1
Vegetables,Organic and locally grown vegetables,Cucumber,Fresh green cucumbers,kg,20.5,2.99,1
Dairy,Milk and dairy products,Milk 2%,2% reduced fat milk,l,120.0,3.49,1
Dairy,Milk and dairy products,Yogurt,Plain Greek yogurt,pack,45.0,4.99,1
Beverages,Soft drinks and juices,Orange Juice,Fresh orange juice,l,35.0,4.99,1
Beverages,Soft drinks and juices,Apple Juice,Fresh apple juice,l,28.0,3.99,1
```

### Example 2: With Empty Descriptions

```csv
category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Snacks,Popular snacks and treats,Chips,Crispy potato chips,pack,50.0,1.99,1
Snacks,Popular snacks and treats,Cookies,,pack,30.0,2.49,1
Frozen,Frozen foods,Ice Cream,Vanilla ice cream,l,20.0,5.99,1
```

### Example 3: Mixed Status

```csv
category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Bakery,Fresh baked goods,Bread,Whole wheat bread,pcs,10.0,3.99,1
Bakery,Fresh baked goods,Donut,Glazed donuts,pcs,0.0,0.99,0
Bakery,Fresh baked goods,Cake,Chocolate cake,pcs,5.0,12.99,1
```

---

## Import Steps

### Method 1: Using the Web Interface

1. **Navigate to Import Tab**
   - Click "📥 Import CSV" in the navigation bar

2. **Select File**
   - Click "📂 Browse Files" button
   - Or drag and drop a CSV file onto the upload area
   - Select your CSV file

3. **Validate CSV**
   - Click "✓ Validate CSV" button
   - Review validation results
   - Check for any errors (shown in red)
   - If valid, proceed to import

4. **Import Data**
   - Click "🚀 Import Data to Database" button
   - Monitor the progress bar
   - Wait for import to complete

5. **Review Results**
   - Check the success summary
   - Note any errors that occurred
   - View created categories and products count

### Method 2: Using API

**Validate CSV:**
```bash
curl -X POST http://localhost:8000/api/import-csv/validate \
  -F "file=@your_file.csv"
```

**Import CSV:**
```bash
curl -X POST http://localhost:8000/api/import-csv \
  -F "file=@your_file.csv"
```

**Download Template:**
```bash
curl http://localhost:8000/api/import-csv/template
```

---

## Validation Process

The validation process checks:

### 1. File Format
- ✓ File is CSV format
- ✓ File is not empty
- ✓ File encoding is valid

### 2. Column Structure
- ✓ All required columns present
- ✓ Column names match exactly (case-sensitive)
- ✓ Correct column order

### 3. Data Types
- ✓ `stock_quantity` is a valid number
- ✓ `selling_price` is a valid number
- ✓ `is_active` is 0 or 1

### 4. Required Fields
- ✓ No empty required fields
- ✓ Category names are not empty
- ✓ Product names are not empty

### 5. Data Range
- ✓ Numbers are within valid ranges
- ✓ Text fields not exceeding limits
- ✓ Prices are positive

**Validation Result Example:**
```json
{
  "status": "valid",
  "row_count": 10,
  "unique_categories": 3,
  "categories": ["Fruits", "Vegetables", "Dairy"],
  "validation_errors": [],
  "error_count": 0,
  "message": "CSV file is valid with 10 rows and 3 categories"
}
```

---

## Error Handling

### Common Errors

**Missing Column**
```
Error: Missing required columns: selling_price, stock_quantity
```
**Solution**: Ensure all 8 columns are present and correctly named

**Invalid Data Type**
```
Row 5: Invalid stock_quantity '25kg'
```
**Solution**: Use only numbers (decimals allowed), e.g., "25.5"

**Invalid is_active Value**
```
Row 3: Invalid is_active '2'
```
**Solution**: Use only 0 or 1

**Duplicate Category Name**
```
Row 8: Duplicate category 'Fruits' already processed
```
**Solution**: Category names must be unique within a single import

**Empty Row**
```
Row 12: Empty row detected
```
**Solution**: Remove empty rows from CSV file

### Error Recovery

1. **Review Error List**
   - Note the row numbers with errors
   - Identify the specific issues

2. **Fix Data**
   - Open CSV in a text editor
   - Correct the problematic rows
   - Save the file

3. **Revalidate**
   - Upload the corrected file
   - Validate again
   - Proceed to import

---

## Best Practices

### 1. File Preparation
- ✓ Use UTF-8 encoding
- ✓ Avoid special characters in category names
- ✓ Keep descriptions concise but meaningful
- ✓ Use consistent units across products
- ✓ Remove any extra blank rows

### 2. Data Quality
- ✓ Verify prices are realistic
- ✓ Ensure stock quantities are accurate
- ✓ Double-check category names for typos
- ✓ Use consistent naming conventions
- ✓ Mark inactive products with 0

### 3. Before Import
- ✓ Always validate before importing
- ✓ Review validation results carefully
- ✓ Keep a backup of the original CSV
- ✓ Test with a small dataset first

### 4. Import Strategy
- ✓ Import categories and products together
- ✓ Don't duplicate category names across imports
- ✓ Update products via individual edit, not re-import
- ✓ Import during off-peak hours for large files

### 5. Post-Import
- ✓ Verify imported data in the Products tab
- ✓ Check dashboard statistics
- ✓ Filter by category to ensure correct associations
- ✓ Update any incorrect prices or stocks

### 6. File Management
- ✓ Keep organized copies of CSV files
- ✓ Name files descriptively: "grocery_import_2024_04.csv"
- ✓ Include date in filename
- ✓ Maintain version history

---

## Creating CSV Files

### Using Spreadsheet Applications

**Google Sheets:**
1. Create spreadsheet with column headers
2. Add data rows
3. File → Download → Comma Separated Values (.csv)

**Microsoft Excel:**
1. Create spreadsheet with column headers
2. Add data rows
3. File → Save As → CSV (Comma delimited)

**Apple Numbers:**
1. Create spreadsheet with column headers
2. Add data rows
3. File → Export → CSV

### Using Text Editors

**Create manually with any text editor:**
```
category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Fruits,Fresh fruits,Apple,Red apples,kg,25.5,3.99,1
```

---

## Download Template

You can download a CSV template directly from the application:

1. Navigate to "📥 Import CSV" tab
2. Scroll to bottom
3. Click "⬇️ Download CSV Template"
4. Template file will download as `grocery_template.csv`
5. Open in spreadsheet application
6. Add your data
7. Save as CSV

---

## Troubleshooting

### File Won't Upload

**Solution:**
- Check file size (max 50MB)
- Ensure file is actually CSV format
- Try different browser

### Validation Keeps Failing

**Solution:**
- Download template and compare format
- Check for special characters in data
- Verify column names match exactly
- Try saving file as UTF-8

### Import Shows Partial Success

**Solution:**
- Review error list for specific rows
- Fix those rows in CSV
- Re-import (won't create duplicates)
- Successfully imported rows won't be re-processed

---

## Support

For issues with CSV import:

1. Check validation error messages
2. Review this guide for data format
3. Download and use the template
4. Contact support with CSV sample (anonymized)

---

**Last Updated:** April 2026
**Version:** 1.0.0
