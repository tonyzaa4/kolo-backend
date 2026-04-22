from pydantic import BaseModel
from typing import Optional
from datetime import date
from typing import Dict

# 1. Схема для отримання даних ВІД клієнта (при реєстрації)
class UserCreate(BaseModel):
    email: str
    password: str

# 2. Схема для відправки даних ДО клієнта (Безпечна!)
class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# --- НОВІ СХЕМИ ДЛЯ КАТАЛОГУ ПІДПИСОК (Спринт 3) ---
class SubscriptionOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    icon_url: Optional[str] = None
    default_price: float
    default_currency: str
    is_custom: bool

# --- Спринт 4 ---
class UserSubscriptionCreate(BaseModel):
    subscription_id: Optional[int] = None  # ID з каталогу (якщо користувач обрав готовий сервіс)
    custom_name: Optional[str] = None  # Власна назва (якщо сервісу немає в базі)
    start_date: Optional[date] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    billing_cycle: Optional[str] = None

class UserSubscriptionOut(BaseModel):
    id: int
    user_id: int
    subscription_id: Optional[int]
    custom_name: Optional[str]
    start_date: Optional[date]
    price: Optional[float]
    currency: Optional[str]
    billing_cycle: Optional[str]
    status: str

    class Config:
        from_attributes = True

class AnalyticsOut(BaseModel):
    total_spend: float
    by_category: Dict[str, float]