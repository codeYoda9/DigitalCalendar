"""Meal planning API routes."""
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/meals", tags=["meals"])

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_week_start(target_date: date) -> date:
    """Get the Monday (start of week) for a given date."""
    return target_date - timedelta(days=target_date.weekday())


@router.get("/week", response_model=schemas.MealWeekData)
def get_weekly_meals(date_param: date = Query(None), db: Session = Depends(get_db)):
    """Get meal plan for a week. If no date provided, returns current week."""
    if date_param is None:
        date_param = datetime.utcnow().date()

    week_start = get_week_start(date_param)
    meals_data = {}

    # Query all meals for this week
    meals = db.query(models.Meal).filter(models.Meal.week_start_date == week_start).all()
    meals_dict = {meal.day_of_week: meal for meal in meals}

    # Build response with all days
    for day in DAYS_OF_WEEK:
        meal = meals_dict.get(day)
        meals_data[day] = schemas.MealDay(
            breakfast=meal.breakfast if meal else None,
            lunch=meal.lunch if meal else None,
            dinner=meal.dinner if meal else None,
        )

    return schemas.MealWeekData(**meals_data)


@router.put("/week", response_model=schemas.MealWeekData)
def update_weekly_meals(
    meals_data: schemas.MealWeekData, date_param: date = Query(None), db: Session = Depends(get_db)
):
    """Update entire week meal plan. If no date provided, updates current week."""
    if date_param is None:
        date_param = datetime.utcnow().date()

    week_start = get_week_start(date_param)

    # Clear existing meals for this week
    db.query(models.Meal).filter(models.Meal.week_start_date == week_start).delete()

    # Insert new meals
    for day in DAYS_OF_WEEK:
        day_meals = getattr(meals_data, day)
        if any([day_meals.breakfast, day_meals.lunch, day_meals.dinner]):
            meal = models.Meal(
                week_start_date=week_start,
                day_of_week=day,
                breakfast=day_meals.breakfast,
                lunch=day_meals.lunch,
                dinner=day_meals.dinner,
            )
            db.add(meal)

    db.commit()
    return meals_data
