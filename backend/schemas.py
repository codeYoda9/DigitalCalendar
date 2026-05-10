"""Pydantic schemas for request/response validation."""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Task Schemas
class TaskBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=255)
    done: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    text: Optional[str] = Field(None, max_length=255)
    done: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Grocery Schemas
class GroceryBase(BaseModel):
    item: str = Field(..., min_length=1, max_length=255)
    checked: bool = False


class GroceryCreate(GroceryBase):
    pass


class GroceryUpdate(BaseModel):
    item: Optional[str] = Field(None, max_length=255)
    checked: Optional[bool] = None


class GroceryResponse(GroceryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Meal Schemas
class MealDay(BaseModel):
    breakfast: Optional[str] = Field(None, max_length=255)
    lunch: Optional[str] = Field(None, max_length=255)
    dinner: Optional[str] = Field(None, max_length=255)


class MealWeekData(BaseModel):
    """Weekly meal plan data."""
    Monday: MealDay
    Tuesday: MealDay
    Wednesday: MealDay
    Thursday: MealDay
    Friday: MealDay
    Saturday: MealDay
    Sunday: MealDay


class MealResponse(BaseModel):
    id: int
    week_start_date: date
    day_of_week: str
    breakfast: Optional[str]
    lunch: Optional[str]
    dinner: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# Calendar Event Schemas
class CalendarEvent(BaseModel):
    """Calendar event response."""
    id: str
    title: str
    start: datetime
    end: datetime
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarEventsResponse(BaseModel):
    """Calendar events for a given date range."""
    events: List[CalendarEvent]
    date: date


# Health check
class HealthResponse(BaseModel):
    status: str
    database: str
