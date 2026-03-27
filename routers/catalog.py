from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Імпортуємо модулі для роботи з БД
import models
from database import get_db
from routers.users import oauth2_scheme

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

# --- Ендпоінт 1: Каталог + Пошук + Категорії (SCRUM-29) ---
@router.get(
    "/",
    summary="Отримати каталог з пошуком та фільтрацією",
    description="Повертає список підписок. Дозволяє шукати за назвою (`search`) та категорією (`category`). **Тільки для авторизованих.**"
)
def get_catalog(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    query = db.query(models.Subscription)

    if search:
        query = query.filter(models.Subscription.name.contains(search))
    if category:
        query = query.filter(models.Subscription.category == category)

    return query.all()


# --- Ендпоінт 2: Фільтрація за ціною (SCRUM-33 + фікс default_price) ---
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

    if min_price is not None and max_price is not None:
        query = query.filter(models.Subscription.default_price.between(min_price, max_price))
    elif min_price is not None:
        query = query.filter(models.Subscription.default_price >= min_price)
    elif max_price is not None:
        query = query.filter(models.Subscription.default_price <= max_price)

    return query.all()


# --- Ендпоінт 3: Деталі однієї підписки (SCRUM-99) ---
@router.get(
    "/{subscription_id}",
    summary="Отримати деталі підписки за ID",
    description="Повертає всю інформацію про одну конкретну підписку за її ID. Потрібно для екрану деталей в Android. **Тільки для авторизованих.**"
)
def get_subscription_by_id(
    subscription_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Підписку не знайдено")
        
    return subscription