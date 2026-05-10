"""Grocery API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/groceries", tags=["groceries"])


@router.get("", response_model=List[schemas.GroceryResponse])
def get_groceries(
    skip: int = 0, limit: int = 100, checked: bool = None, db: Session = Depends(get_db)
):
    """Get all grocery items, optionally filtered by checked status."""
    query = db.query(models.Grocery)
    if checked is not None:
        query = query.filter(models.Grocery.checked == checked)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=schemas.GroceryResponse, status_code=201)
def create_grocery(grocery: schemas.GroceryCreate, db: Session = Depends(get_db)):
    """Create a new grocery item."""
    db_grocery = models.Grocery(**grocery.dict())
    db.add(db_grocery)
    db.commit()
    db.refresh(db_grocery)
    return db_grocery


@router.patch("/{grocery_id}", response_model=schemas.GroceryResponse)
def update_grocery(
    grocery_id: int,
    grocery_update: schemas.GroceryUpdate,
    db: Session = Depends(get_db),
):
    """Update a grocery item."""
    db_grocery = db.query(models.Grocery).filter(models.Grocery.id == grocery_id).first()
    if not db_grocery:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    update_data = grocery_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_grocery, field, value)

    db.add(db_grocery)
    db.commit()
    db.refresh(db_grocery)
    return db_grocery


@router.delete("/{grocery_id}", status_code=204)
def delete_grocery(grocery_id: int, db: Session = Depends(get_db)):
    """Delete a grocery item."""
    db_grocery = db.query(models.Grocery).filter(models.Grocery.id == grocery_id).first()
    if not db_grocery:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    db.delete(db_grocery)
    db.commit()
    return None
