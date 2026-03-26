from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Імпортуємо модулі для роботи з БД
import models
from database import get_db
from routers.users import oauth2_scheme

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

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
    # 1. Починаємо формувати запит до таблиці Subscription
    query = db.query(models.Subscription)

    # 2. Якщо передали параметр search, фільтруємо по назві (як просили в тасці)
    if search:
        query = query.filter(models.Subscription.name.contains(search))

    # 3. Якщо передали параметр category, фільтруємо по категорії
    if category:
        query = query.filter(models.Subscription.category == category)

    # 4. Виконуємо запит і віддаємо результати
    return query.all()