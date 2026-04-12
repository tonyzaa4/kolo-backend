from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Імпортуємо наші моделі та підключення до БД
import models
from database import get_db

# Створюємо роутер із префіксом
router = APIRouter(prefix="/api/exchange-rates", tags=["Currency"])

@router.get(
    "/",
    summary="Отримати поточні курси валют",
    description="Віддає мобільному додатку всі збережені курси валют з бази даних."
)
def get_exchange_rates(db: Session = Depends(get_db)):
    # Просто дістаємо всі записи з таблиці ExchangeRate і повертаємо їх
    rates = db.query(models.ExchangeRate).all()
    return rates
