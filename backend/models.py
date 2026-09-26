"""SQLAlchemy models for database tables."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from database import Base


class Task(Base):
    """Task model for shared todo list."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    done = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class Grocery(Base):
    """Grocery model for shared shopping list."""
    __tablename__ = "groceries"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String(255), nullable=False)
    checked = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
