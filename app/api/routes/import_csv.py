from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
import csv
import io
import logging

from app.core.mysql_database.mysql_service import get_mysql_service
from app.core.mysql_database.mysql_manager import MySQLManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["import"])


@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...), db: MySQLManager = Depends(get_mysql_service)):
    """
    Import inventory data from CSV file and populate the database.
    
    CSV Format:
    category_name, category_description, product_name, product_description, unit, stock_quantity, selling_price, is_active
    
    Example:
    Fruits,Fresh fruits,Apple,Red apples,kg,25.5,3.99,1
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read the CSV file
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        if not csv_reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Validate required columns
        required_columns = {
            'category_name', 'category_description', 'product_name', 
            'product_description', 'unit', 'stock_quantity', 'selling_price', 'is_active'
        }
        
        csv_columns = set(csv_reader.fieldnames)
        if not required_columns.issubset(csv_columns):
            missing = required_columns - csv_columns
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing)}"
            )
        
        # Process the CSV data
        categories_created = {}
        products_created = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 because row 1 is header
            try:
                # Clean up whitespace
                row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                
                category_name = row['category_name']
                category_description = row['category_description']
                product_name = row['product_name']
                product_description = row['product_description']
                unit = row['unit']
                
                try:
                    stock_quantity = float(row['stock_quantity'])
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid stock_quantity '{row['stock_quantity']}'")
                    continue
                
                try:
                    selling_price = float(row['selling_price'])
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid selling_price '{row['selling_price']}'")
                    continue
                
                try:
                    is_active = int(row['is_active'])
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid is_active '{row['is_active']}'")
                    continue
                
                # Create category if it doesn't exist
                if category_name not in categories_created:
                    try:
                        category_id = db.create_category(
                            name=category_name,
                            description=category_description
                        )
                        categories_created[category_name] = category_id
                        logger.info(f"Created category: {category_name} (ID: {category_id})")
                    except Exception as e:
                        # Category might already exist, try to fetch it
                        try:
                            existing_categories = db.get_all_categories()
                            for cat in existing_categories:
                                if cat.get('name') == category_name:
                                    categories_created[category_name] = cat['id']
                                    break
                            else:
                                errors.append(f"Row {row_num}: Failed to create/find category '{category_name}': {str(e)}")
                                continue
                        except Exception as e2:
                            errors.append(f"Row {row_num}: Error with category '{category_name}': {str(e2)}")
                            continue
                
                category_id = categories_created.get(category_name)
                
                if not category_id:
                    errors.append(f"Row {row_num}: Could not resolve category '{category_name}'")
                    continue
                
                # Create product
                try:
                    product_id = db.create_product(
                        name=product_name,
                        description=product_description,
                        category_id=category_id,
                        unit=unit,
                        stock_quantity=stock_quantity,
                        selling_price=selling_price,
                        is_active=bool(is_active)
                    )
                    products_created += 1
                    logger.info(f"Created product: {product_name} (ID: {product_id})")
                except Exception as e:
                    errors.append(f"Row {row_num}: Failed to create product '{product_name}': {str(e)}")
                    continue
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Unexpected error: {str(e)}")
                continue
        
        # Prepare response
        response_data = {
            "status": "success",
            "categories_created": len(categories_created),
            "products_created": products_created,
            "errors": errors,
            "error_count": len(errors),
            "categories": list(categories_created.keys()),
            "message": f"Successfully imported {products_created} products from {len(categories_created)} categories"
        }
        
        if errors:
            response_data["status"] = "partial"
            response_data["message"] = f"Imported {products_created} products with {len(errors)} errors. See 'errors' for details."
        
        logger.info(f"CSV import completed: {products_created} products, {len(categories_created)} categories, {len(errors)} errors")
        
        return JSONResponse(status_code=200, content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/import-csv/template")
async def get_csv_template():
    """
    Get a CSV template for importing inventory data.
    """
    template = """category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Fruits,Fresh and seasonal fruits,Apple,Red delicious apples,kg,25.5,3.99,1
Fruits,Fresh and seasonal fruits,Banana,Ripe Cavendish bananas,kg,40.2,2.49,1
Vegetables,Organic and locally grown vegetables,Tomato,Vine-ripened tomatoes,kg,32.0,3.79,1
Dairy,Milk and dairy products,Milk 2%,2% reduced fat milk,l,120.0,3.49,1
Beverages,Soft drinks and juices,Orange Juice,Fresh orange juice,l,35.0,4.99,1"""
    
    return JSONResponse(
        status_code=200,
        content={
            "template": template,
            "description": "CSV template for importing inventory",
            "required_columns": [
                "category_name",
                "category_description",
                "product_name",
                "product_description",
                "unit",
                "stock_quantity",
                "selling_price",
                "is_active"
            ]
        }
    )


@router.post("/import-csv/validate")
async def validate_csv(file: UploadFile = File(...)):
    """
    Validate a CSV file without importing it.
    Returns detailed validation results.
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        if not csv_reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        required_columns = {
            'category_name', 'category_description', 'product_name', 
            'product_description', 'unit', 'stock_quantity', 'selling_price', 'is_active'
        }
        
        csv_columns = set(csv_reader.fieldnames)
        missing_columns = required_columns - csv_columns
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Validate rows
        row_count = 0
        validation_errors = []
        categories = set()
        
        for row_num, row in enumerate(csv_reader, start=2):
            row_count += 1
            
            # Check for empty rows
            if not any(row.values()):
                validation_errors.append(f"Row {row_num}: Empty row")
                continue
            
            # Validate numeric fields
            try:
                float(row['stock_quantity'])
            except (ValueError, TypeError):
                validation_errors.append(f"Row {row_num}: Invalid stock_quantity '{row['stock_quantity']}'")
            
            try:
                float(row['selling_price'])
            except (ValueError, TypeError):
                validation_errors.append(f"Row {row_num}: Invalid selling_price '{row['selling_price']}'")
            
            try:
                int(row['is_active'])
            except (ValueError, TypeError):
                validation_errors.append(f"Row {row_num}: Invalid is_active '{row['is_active']}'")
            
            # Collect category names
            categories.add(row['category_name'].strip())
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "valid" if not validation_errors else "invalid",
                "row_count": row_count,
                "unique_categories": len(categories),
                "categories": list(categories),
                "validation_errors": validation_errors,
                "error_count": len(validation_errors),
                "message": f"CSV file is valid with {row_count} rows and {len(categories)} categories" if not validation_errors else f"CSV file has {len(validation_errors)} validation errors"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating CSV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating CSV file: {str(e)}"
        )
