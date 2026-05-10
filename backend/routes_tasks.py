"""Task API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[schemas.TaskResponse])
def get_tasks(
    skip: int = 0, limit: int = 100, done: bool = None, db: Session = Depends(get_db)
):
    """Get all tasks, optionally filtered by completion status."""
    query = db.query(models.Task)
    if done is not None:
        query = query.filter(models.Task.done == done)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)
):
    """Update a task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return None
