"""Import all models so SQLAlchemy and Alembic can discover them."""

from app.models.user import User
from app.models.food import Food
from app.models.food_log import FoodLog
from app.models.weight_log import WeightLog
from app.models.friendship import Friendship
from app.models.pk_battle import PKBattle

__all__ = [
    "User",
    "Food",
    "FoodLog",
    "WeightLog",
    "Friendship",
    "PKBattle",
]
