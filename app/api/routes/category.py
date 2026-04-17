from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
import os
from app.core.mysql_database.mysql_manager import MySQLManager
from app.core.mysql_database.mysql_service import get_mysql_service

router = APIRouter(prefix="/categories", tags=["categories"])


from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: MySQLManager = Depends(get_mysql_service)):
    """Create a new category."""
    try:
        category_id = db.create_category(
            name=category.name,
            description=category.description
        )
        result = db.get_category(category_id)
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to create category")
    except Exception as e:
        if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Category name already exists")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: MySQLManager = Depends(get_mysql_service)):
    """Get a category by ID."""
    try:
        result = db.get_category(category_id)
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return result
    finally:
        db.close()


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: MySQLManager = Depends(get_mysql_service)):
    """Get all categories."""
    try:
        results = db.get_all_categories()
        return results
    finally:
        db.close()


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: MySQLManager = Depends(get_mysql_service)):
    """Update a category."""
    try:
        # Check if category exists
        existing = db.get_category(category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Category not found")

        # Update the category
        success = db.update_category(
            category_id=category_id,
            name=category.name,
            description=category.description
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update category")

        result = db.get_category(category_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Category name already exists")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: MySQLManager = Depends(get_mysql_service)):
    """Delete a category."""
    try:
        # Check if category exists
        existing = db.get_category(category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Category not found")

        success = db.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete category")
    except HTTPException:
        raise
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e) or "Cannot delete" in str(e):
            raise HTTPException(status_code=400, detail="Cannot delete category with existing products")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
