from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Імпортуємо модулі для роботи з БД
import models
from database import get_db
from routers.users import oauth2_scheme

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

# --- Ендпоінт 1 (з попередньої таски SCRUM-29) ---
@router.get(
    "/",
    summary="Отримати каталог з пошуком та фільтрацією",
    description="Повертає список підписок. Дозволяє шукати за назвою (`search`) та категорією (`category`). **Тільки для авторизованих.**"
)
def get_catalog(
    search: Optional[str] = None,          # Query-параметр для пошуку
    category: Optional[str] = None,        # Query-параметр для категорії
    db: Session = Depends(get_db),         # Підключення до бази даних
    token: str = Depends(oauth2_scheme)    # Наш фейсконтроль (JWT)
):
    # Починаємо формувати запит до таблиці Subscription
    query = db.query(models.Subscription)

    # Якщо передали параметр search, фільтруємо по назві
    if search:
        query = query.filter(models.Subscription.name.contains(search))

    # Якщо передали параметр category, фільтруємо по категорії
    if category:
        query = query.filter(models.Subscription.category == category)

    # Виконуємо запит і віддаємо результати
    return query.all()


# --- Ендпоінт 2 (НОВИЙ, для поточної таски SCRUM-33) ---
@router.get(
    "/price-range",
    summary="Отримати підписки за діапазоном цін",
    description="Повертає список підписок у заданому діапазоні цін (`min_price` - `max_price`). **Тільки для авторизованих.**"
)
def get_subscriptions_by_price(
    min_price: Optional[float] = None,      
    max_price: Optional[float] = None,      
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    query = db.query(models.Subscription)

    # ВИПРАВЛЕНО: замінили price на default_price
    if min_price is not None and max_price is not None:
        query = query.filter(models.Subscription.default_price.between(min_price, max_price))
    elif min_price is not None:
        query = query.filter(models.Subscription.default_price >= min_price)
    elif max_price is not None:
        query = query.filter(models.Subscription.default_price <= max_price)

    return query.all()