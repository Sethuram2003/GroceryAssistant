from fastapi import APIRouter, HTTPException, Depends, Query, Depends
from typing import Optional, List
import os
from app.core.mysql_database.mysql_service import get_mysql_service
from app.core.mysql_database.mysql_manager import MySQLManager


from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    unit: str = "pcs"
    stock_quantity: float = 0.0
    selling_price: float
    is_active: int = 1

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit: Optional[str] = None
    stock_quantity: Optional[float] = None
    selling_price: Optional[float] = None
    is_active: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    unit: str
    stock_quantity: float
    selling_price: float
    is_active: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: MySQLManager = Depends(get_mysql_service)):
    """Create a new product."""
    try:
        product_id = db.create_product(
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            unit=product.unit,
            stock_quantity=product.stock_quantity,
            selling_price=product.selling_price,
            is_active=product.is_active
        )
        result = db.get_product(product_id)
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to create product")
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e) or "Cannot add" in str(e):
            raise HTTPException(status_code=400, detail="Invalid category_id")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: MySQLManager = Depends(get_mysql_service)):
    """Get a product by ID."""
    try:
        result = db.get_product(product_id)
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        return result
    finally:
        db.close()


@router.get("/", response_model=List[ProductResponse])
def get_all_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_active: Optional[int] = Query(None, description="Filter by active status (0 or 1)"),
    db: MySQLManager = Depends(get_mysql_service)
):
    """Get all products with optional filtering."""
    try:
        results = db.get_all_products(category_id=category_id, is_active=is_active)
        return results
    finally:
        db.close()


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: MySQLManager = Depends(get_mysql_service)):
    """Update a product."""
    try:
        # Check if product exists
        existing = db.get_product(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update the product
        success = db.update_product(
            product_id=product_id,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            unit=product.unit,
            stock_quantity=product.stock_quantity,
            selling_price=product.selling_price,
            is_active=product.is_active
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update product")

        result = db.get_product(product_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e) or "Cannot add" in str(e):
            raise HTTPException(status_code=400, detail="Invalid category_id")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: MySQLManager = Depends(get_mysql_service)):
    """Delete a product."""
    try:
        # Check if product exists
        existing = db.get_product(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        success = db.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete product")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
