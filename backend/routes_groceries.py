"""Grocery API routes."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from crud_helpers import (
    create_record,
    delete_record,
    get_record_or_404,
    list_records,
    update_record,
)
from database import get_db

router = APIRouter(prefix="/api/groceries", tags=["groceries"])


@router.get("", response_model=List[schemas.GroceryResponse])
def get_groceries(
    skip: int = 0, limit: int = 100, checked: bool = None, db: Session = Depends(get_db)
):
    """Get all grocery items, optionally filtered by checked status."""
    return list_records(db, models.Grocery, "checked", checked, skip, limit)


@router.post("", response_model=schemas.GroceryResponse, status_code=201)
def create_grocery(grocery: schemas.GroceryCreate, db: Session = Depends(get_db)):
    """Create a new grocery item."""
    return create_record(db, models.Grocery, grocery)


@router.patch("/{grocery_id}", response_model=schemas.GroceryResponse)
def update_grocery(
    grocery_id: int,
    grocery_update: schemas.GroceryUpdate,
    db: Session = Depends(get_db),
):
    """Update a grocery item."""
    db_grocery = get_record_or_404(db, models.Grocery, grocery_id, "Grocery item not found")
    return update_record(db, db_grocery, grocery_update)


@router.delete("/{grocery_id}", status_code=204)
def delete_grocery(grocery_id: int, db: Session = Depends(get_db)):
    """Delete a grocery item."""
    db_grocery = get_record_or_404(db, models.Grocery, grocery_id, "Grocery item not found")
    delete_record(db, db_grocery)
    return None
