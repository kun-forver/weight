"""Dashboard router: returns all data for the homepage in one call."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food_log import FoodLog
from app.models.food import Food
from app.models.pk_battle import PKBattle
from app.models.user import User
from app.models.weight_log import WeightLog
from app.services.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def generate_dashboard_data(user: User, db: Session) -> dict:
    """Compute dashboard data for a given user."""
    # --- Today's food logs ---
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    logs = (
        db.query(FoodLog, Food.name)
        .join(Food, FoodLog.food_id == Food.id, isouter=True)
        .filter(
            FoodLog.user_id == user.id,
            FoodLog.logged_at >= today_start,
            FoodLog.logged_at < today_end,
        )
        .all()
    )

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    meals: dict[int, list] = {0: [], 1: [], 2: [], 3: []}

    for log, food_name in logs:
        total_calories += log.calories or 0
        total_protein += log.protein or 0
        total_carbs += log.carbs or 0
        total_fat += log.fat or 0
        if log.meal_type in meals:
            meals[log.meal_type].append({
                "id": log.id,
                "food_id": log.food_id,
                "food_name": food_name,
                "amount": log.amount,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fat": log.fat,
                "meal_type": log.meal_type,
                "logged_at": log.logged_at.isoformat() if log.logged_at else None,
            })

    # --- Calorie goal ---
    calorie_goal = user.daily_calorie_goal or 2000
    remaining_calories = calorie_goal - total_calories

    # --- Estimated nutrition targets (based on calorie goal) ---
    # Rough split: protein 25%, carbs 50%, fat 25% of calories
    # Protein: 4 kcal/g, Carbs: 4 kcal/g, Fat: 9 kcal/g
    target_protein = round(calorie_goal * 0.25 / 4, 1)
    target_carbs = round(calorie_goal * 0.5 / 4, 1)
    target_fat = round(calorie_goal * 0.25 / 9, 1)

    # --- Weight data ---
    latest_weight_log = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id)
        .order_by(WeightLog.logged_at.desc())
        .first()
    )
    previous_weight_log = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id)
        .order_by(WeightLog.logged_at.desc())
        .offset(1)
        .first()
    )

    latest_weight = latest_weight_log.weight if latest_weight_log else None
    previous_weight = previous_weight_log.weight if previous_weight_log else None
    weight_change = round(latest_weight - previous_weight, 2) if (latest_weight and previous_weight) else None

    # --- Active PK battle ---
    active_battle = (
        db.query(PKBattle)
        .filter(
            PKBattle.status.in_([0, 1]),
            (PKBattle.user_a == user.id) | (PKBattle.user_b == user.id),
        )
        .order_by(PKBattle.created_at.desc())
        .first()
    )

    pk_data = None
    if active_battle:
        from app.routers.pk import _get_battle_details_helper
        pk_data = _get_battle_details_helper(active_battle, db).model_dump()

    # --- Today's check-in status ---
    today_weight_log = (
        db.query(WeightLog)
        .filter(
            WeightLog.user_id == user.id,
            WeightLog.logged_at >= today_start,
            WeightLog.logged_at < today_end,
        )
        .first()
    )

    return {
        "date": date.today().isoformat(),
        "calorie_summary": {
            "goal": calorie_goal,
            "consumed": round(total_calories, 1),
            "remaining": round(remaining_calories, 1),
            "exercise": 0,  # placeholder for future exercise tracking
        },
        "nutrition_breakdown": {
            "protein": {"current": round(total_protein, 1), "target": target_protein},
            "carbs": {"current": round(total_carbs, 1), "target": target_carbs},
            "fat": {"current": round(total_fat, 1), "target": target_fat},
        },
        "weight": {
            "latest": latest_weight,
            "previous": previous_weight,
            "change": weight_change,
            "target_weight": user.target_weight,
            "checked_in_today": today_weight_log is not None,
            "body_fat": latest_weight_log.body_fat if latest_weight_log else None,
            "muscle": latest_weight_log.muscle if latest_weight_log else None,
        },
        "meals": {
            "breakfast": meals[0],
            "lunch": meals[1],
            "dinner": meals[2],
            "snack": meals[3],
        },
        "pk": pk_data,
    }


@router.get("")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all data for the homepage dashboard."""
    return generate_dashboard_data(current_user, db)
