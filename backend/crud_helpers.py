"""Shared CRUD helpers for simple SQLAlchemy-backed resources."""
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session


def schema_data(schema: Any) -> dict[str, Any]:
    if hasattr(schema, "model_dump"):
        return schema.model_dump(exclude_unset=True)
    return schema.dict(exclude_unset=True)


def list_records(
    db: Session,
    model: Any,
    filter_field: str,
    filter_value: Any,
    skip: int,
    limit: int,
):
    query = db.query(model)
    if filter_value is not None:
        query = query.filter(getattr(model, filter_field) == filter_value)
    return query.offset(skip).limit(limit).all()


def create_record(db: Session, model: Any, payload: Any):
    db_record = model(**schema_data(payload))
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_record_or_404(db: Session, model: Any, record_id: int, detail: str):
    db_record = db.query(model).filter(model.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail=detail)
    return db_record


def update_record(db: Session, db_record: Any, payload: Any):
    for field, value in schema_data(payload).items():
        setattr(db_record, field, value)

    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_record(db: Session, db_record: Any):
    db.delete(db_record)
    db.commit()
