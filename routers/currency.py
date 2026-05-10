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
    description="Віддає мобільному клієнту список усіх кешованих курсів валют (USD, EUR по відношенню до UAH), оновлених планувальником з API Національного банку України."
)
def get_exchange_rates(db: Session = Depends(get_db)):
    # Просто дістаємо всі записи з таблиці ExchangeRate і повертаємо їх
    rates = db.query(models.ExchangeRate).all()
    return rates