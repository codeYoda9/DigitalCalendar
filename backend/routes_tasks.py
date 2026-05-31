"""Task API routes."""
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

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[schemas.TaskResponse])
def get_tasks(
    skip: int = 0, limit: int = 100, done: bool = None, db: Session = Depends(get_db)
):
    """Get all tasks, optionally filtered by completion status."""
    return list_records(db, models.Task, "done", done, skip, limit)


@router.post("", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    return create_record(db, models.Task, task)


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)
):
    """Update a task."""
    db_task = get_record_or_404(db, models.Task, task_id, "Task not found")
    return update_record(db, db_task, task_update)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    db_task = get_record_or_404(db, models.Task, task_id, "Task not found")
    delete_record(db, db_task)
    return None
