"""Food router: search foods, manage custom foods, and food logs."""

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food import Food
from app.models.food_log import FoodLog
from app.models.user import User
from app.schemas.food import (
    FoodLogCreate,
    FoodLogResponse,
    FoodLogSummary,
    FoodResponse,
)
from app.services.auth import get_current_user
from app.services.food_api import off_service

router = APIRouter(prefix="", tags=["food"])


@router.get("/foods/search", response_model=list[FoodResponse])
async def search_foods(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for foods. Searches local DB first, then OpenFoodFacts API."""
    query_str = q.strip() if q else ""
    if not query_str:
        return []

    # 1. Search local DB
    local_foods = (
        db.query(Food)
        .filter(Food.name.like(f"%{query_str}%"))
        .limit(20)
        .all()
    )
    results = [
        FoodResponse(
            id=f.id,
            name=f.name,
            category=f.category,
            calories=f.calories,
            protein=f.protein,
            carbs=f.carbs,
            fat=f.fat,
            is_custom=f.is_custom,
            source="local",
        )
        for f in local_foods
    ]

    # 2. If fewer than 10 local results, supplement with OpenFoodFacts
    if len(results) < 10:
        try:
            off_results = await off_service.search(query_str)
            existing_names = {r.name for r in results}
            for item in off_results:
                if item.get("name") and item["name"] not in existing_names:
                    results.append(
                        FoodResponse(
                            name=item["name"],
                            calories=item.get("calories", 0.0),
                            protein=item.get("protein", 0.0),
                            carbs=item.get("carbs", 0.0),
                            fat=item.get("fat", 0.0),
                            source="openfoodfacts",
                        )
                    )
                if len(results) >= 20:
                    break
        except Exception:
            pass
    return results


@router.post("/foods/custom", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_custom_food(
    food_data: FoodResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a custom food item."""
    food = Food(
        name=food_data.name,
        category=food_data.category,
        calories=food_data.calories,
        protein=food_data.protein,
        carbs=food_data.carbs,
        fat=food_data.fat,
        is_custom=True,
        creator_id=current_user.id,
    )
    db.add(food)
    db.commit()
    db.refresh(food)
    return FoodResponse(
        id=food.id,
        name=food.name,
        category=food.category,
        calories=food.calories,
        protein=food.protein,
        carbs=food.carbs,
        fat=food.fat,
        is_custom=True,
        source="local",
    )


@router.get("/food-logs", response_model=list[FoodLogResponse])
def get_food_logs(
    date_str: str = Query(..., alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all food logs for a given date (YYYY-MM-DD)."""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)

    logs = (
        db.query(FoodLog, Food.name)
        .join(Food, FoodLog.food_id == Food.id, isouter=True)
        .filter(
            FoodLog.user_id == current_user.id,
            FoodLog.logged_at >= start_dt,
            FoodLog.logged_at < end_dt,
        )
        .all()
    )

    result = []
    for log, food_name in logs:
        resp = FoodLogResponse.model_validate(log)
        resp.food_name = food_name
        result.append(resp)
    return result


@router.post("/food-logs", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
def create_food_log(
    payload: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new food log entry."""
    # If food_id is provided, verify it exists; if food_name is provided, create/find custom food
    food_id = payload.food_id
    food_name = payload.food_name
    if food_id is None and food_name:
        # Try to find existing food by name
        existing = db.query(Food).filter(Food.name == food_name).first()
        if existing:
            food_id = existing.id
        else:
            # Create a custom food on the fly
            new_food = Food(
                name=food_name,
                category="自定义",
                calories=payload.calories,
                protein=payload.protein,
                carbs=payload.carbs,
                fat=payload.fat,
                is_custom=True,
                creator_id=current_user.id,
            )
            db.add(new_food)
            db.flush()
            food_id = new_food.id

    if food_id is None:
        raise HTTPException(status_code=400, detail="Either food_id or food_name is required")

    # Auto-calculate calories and macros from food record if not provided
    food = db.query(Food).filter(Food.id == food_id).first()
    calories = payload.calories
    protein = payload.protein
    carbs = payload.carbs
    fat = payload.fat
    if food and calories == 0:
        ratio = payload.amount / 100
        calories = food.calories * ratio
        protein = food.protein * ratio if food.protein else None
        carbs = food.carbs * ratio if food.carbs else None
        fat = food.fat * ratio if food.fat else None

    log = FoodLog(
        user_id=current_user.id,
        food_id=food_id,
        meal_type=payload.meal_type,
        amount=payload.amount,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    resp = FoodLogResponse.model_validate(log)
    resp.food_name = food.name if food else food_name
    return resp


@router.delete("/food-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a food log entry by ID."""
    log = (
        db.query(FoodLog)
        .filter(FoodLog.id == log_id, FoodLog.user_id == current_user.id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    db.delete(log)
    db.commit()


@router.get("/food-logs/summary", response_model=list[FoodLogSummary])
def get_food_log_summary(
    date_str: str = Query(..., alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get daily food log summary per meal type (calories, protein, carbs, fat)."""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)

    logs = (
        db.query(FoodLog)
        .filter(
            FoodLog.user_id == current_user.id,
            FoodLog.logged_at >= start_dt,
            FoodLog.logged_at < end_dt,
        )
        .all()
    )

    # Aggregate per meal type
    summaries: dict[int, dict] = {}
    for log in logs:
        if log.meal_type not in summaries:
            summaries[log.meal_type] = {
                "meal_type": log.meal_type,
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0,
                "count": 0,
            }
        s = summaries[log.meal_type]
        s["total_calories"] += log.calories or 0
        s["total_protein"] += log.protein or 0
        s["total_carbs"] += log.carbs or 0
        s["total_fat"] += log.fat or 0
        s["count"] += 1

    return [FoodLogSummary(**v) for v in summaries.values()]
